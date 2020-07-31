#!/usr/bin/python3

from systems.rbsc import process_rbsc_changes
from systems.embark import process_embark_changes


if __name__ == "__main__":
    process_rbsc_changes()
    process_embark_changes()
