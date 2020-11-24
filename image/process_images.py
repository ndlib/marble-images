#!/usr/bin/python3
import os
import shared.config as config
from systems.rbsc import process_rbsc_changes
from systems.embark import process_embark_changes


if __name__ == "__main__":
    if not os.path.exists(config.EC2_PROCESS_DIR):
        os.makedirs(config.EC2_PROCESS_DIR)
    os.chdir(config.EC2_PROCESS_DIR)
    process_rbsc_changes()
    process_embark_changes()
