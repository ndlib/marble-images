#!/usr/bin/python3
import os
from shared import config
from shared import graphql_utility as gql
from systems.rbsc import process_rbsc_changes
from systems.museum import process_museum_changes
from systems.uri import process_uri_changes


if __name__ == "__main__":
    if not os.path.exists(config.EC2_PROCESS_DIR):
        os.makedirs(config.EC2_PROCESS_DIR)
    os.chdir(config.EC2_PROCESS_DIR)
    todos = gql.generate_image_lists()
    process_rbsc_changes(todos[config.S3])
    process_museum_changes(todos[config.MUSEUM])
    process_uri_changes(todos[config.URI])
    process_uri_changes(todos[config.CURATE])
