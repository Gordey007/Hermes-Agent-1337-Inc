"""Recreates the leads table. Uses a single db.py file.

To run: python 01_x_lead/create_db.py [--keep]
By default, DROP + CREATE (complete rebuild). With --keep, only CREATE IF NOT EXISTS.
"""
import sys

from db import init_db

if __name__ == "__main__":
    keep = "--keep" in sys.argv
    init_db(drop=not keep)
