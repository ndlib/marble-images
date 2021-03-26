#!/usr/bin/python3
import os
from shared import config
from shared import graphql_utility as gql
from systems.default import process_image_changes


if __name__ == "__main__":
    if not os.path.exists(config.EC2_PROCESS_DIR):
        os.makedirs(config.EC2_PROCESS_DIR)
    os.chdir(config.EC2_PROCESS_DIR)
    todos = gql.generate_image_lists()
    process_image_changes(todos)
