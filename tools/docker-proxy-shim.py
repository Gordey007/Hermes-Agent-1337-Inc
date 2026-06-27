#!/usr/bin/env python3
"""
docker-proxy-shim.py — bridge: Docker CLI -> OpenShell forward proxy -> dockerd.

Inside the OpenShell sandbox direct egress is blocked: all traffic must go
through the gateway forward proxy (10.200.0.1:3128), which inspects the L7 REST
calls and enforces the network policy. The Docker CLI, however, talks to the
daemon over raw TCP and does not understand HTTP proxies. This shim closes the
gap:

    docker CLI --(unix /tmp/docker.sock)--> shim
        --(HTTP forward-proxy 10.200.0.1:3128)--> dockerd 172.18.0.1:443

For every client request the shim:
  * reads the request line + headers;
  * rewrites the origin-form path into an absolute-URI (http://DAEMON/<path>);
  * forces Connection: close (one request per upstream connection — simple and
    reliable for chunked/stream/hijack responses);
  * then does a raw bidirectional relay (covers the request body, chunked
    responses, and 101 Upgrade/hijack used by attach/exec/build).

Run:
    nohup python3 tools/docker-proxy-shim.py >/tmp/shim.log 2>&1 &
    export DOCKER_HOST=unix:///tmp/docker.sock
    docker ps

Configurable via env:
    SHIM_SOCK    unix socket path          (default /tmp/docker.sock)
    SHIM_PROXY   host:port forward proxy   (default 10.200.0.1:3128)
    SHIM_DAEMON  host:port dockerd         (default 172.18.0.1:443)
"""
import os
import socket
import threading
import sys

SOCK_PATH = os.environ.get("SHIM_SOCK", "/tmp/docker.sock")
PROXY_HOST, PROXY_PORT = (os.environ.get("SHIM_PROXY", "10.200.0.1:3128").split(":") + ["3128"])[:2]
DAEMON = os.environ.get("SHIM_DAEMON", "172.18.0.1:443")
PROXY_PORT = int(PROXY_PORT)


def log(*a):
    print("[shim]", *a, file=sys.stderr, flush=True)


def pipe(src, dst):
    try:
        while True:
            data = src.recv(65536)
            if not data:
                break
            dst.sendall(data)
    except OSError:
        pass
    finally:
        for s in (src, dst):
            try:
                s.shutdown(socket.SHUT_WR)
            except OSError:
                pass


def read_headers(conn):
    """Read until the end of headers; return (head_bytes, leftover_bytes)."""
    buf = b""
    while b"\r\n\r\n" not in buf:
        chunk = conn.recv(4096)
        if not chunk:
            break
        buf += chunk
        if len(buf) > 1 << 20:  # guard against garbage
            break
    head, sep, rest = buf.partition(b"\r\n\r\n")
    return head + sep, rest


def rewrite(head):
    lines = head.split(b"\r\n")
    try:
        method, path, ver = lines[0].split(b" ", 2)
    except ValueError:
        return None
    if path.startswith(b"http://") or path.startswith(b"https://"):
        new_line = lines[0]
    else:
        new_line = b"%s http://%s%s %s" % (method, DAEMON.encode(), path, ver)
    out = [new_line]
    for h in lines[1:]:
        low = h.lower()
        if low.startswith(b"connection:") or low.startswith(b"proxy-connection:") or low.startswith(b"keep-alive:"):
            continue
        out.append(h)
    # the last element is b'' from the trailing \r\n\r\n split — drop empties, re-add terminator
    out = [x for x in out if x != b""]
    out.append(b"Connection: close")
    return b"\r\n".join(out) + b"\r\n\r\n"


def handle(client):
    upstream = None
    try:
        head, leftover = read_headers(client)
        if not head:
            return
        new_head = rewrite(head)
        if new_head is None:
            return
        upstream = socket.create_connection((PROXY_HOST, PROXY_PORT), timeout=30)
        upstream.settimeout(None)
        upstream.sendall(new_head)
        if leftover:
            upstream.sendall(leftover)
        t = threading.Thread(target=pipe, args=(client, upstream), daemon=True)
        t.start()
        pipe(upstream, client)
        t.join()
    except OSError as e:
        log("error:", e)
    finally:
        for s in (client, upstream):
            if s:
                try:
                    s.close()
                except OSError:
                    pass


def main():
    if os.path.exists(SOCK_PATH):
        os.unlink(SOCK_PATH)
    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    srv.bind(SOCK_PATH)
    os.chmod(SOCK_PATH, 0o660)
    srv.listen(128)
    log(f"listening {SOCK_PATH} -> proxy {PROXY_HOST}:{PROXY_PORT} -> daemon {DAEMON}")
    while True:
        client, _ = srv.accept()
        threading.Thread(target=handle, args=(client,), daemon=True).start()


if __name__ == "__main__":
    main()
