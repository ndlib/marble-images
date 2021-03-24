from . import graphql
from . import config


def _query_files_to_process(nextToken: str = None) -> dict:
    operation = """
        query listFilesToProcess($token: String) {
            listFilesToProcess(nextToken: $token) {
                nextToken
                items {
                    id
                    sourceType
                    sourceFilePath
                    sourceBucketName
                    filePath
                    copyrightStatus
                    sourceUri
                }
            }
        }"""
    operation_name = "listFilesToProcess"
    variables = {"token": nextToken}
    return graphql.run_operation(operation, operation_name, variables)


def _mutate_item_mod_date(item_id: str) -> dict:
    operation = """
        mutation saveFileLastProcessedDate($input: String!) {
            saveFileLastProcessedDate(itemId: $input) {
                id
                modifiedDate
                dateLastProcessed
            }
        }"""
    operation_name = "saveFileLastProcessedDate"
    variables = {"input": item_id}
    return graphql.run_operation(operation, operation_name, variables)


def update_processed_date(item_id: str) -> None:
    return _mutate_item_mod_date(item_id)


def generate_image_lists():
    image_sources = {key: list([]) for key in config.IMAGE_SOURCES}
    todos = _query_files_to_process()
    for todo in todos['data']['listFilesToProcess']['items']:
        image_sources.get(todo['sourceType']).append(todo)
    nextToken = todos['data']['listFilesToProcess']['nextToken']
    while nextToken:
        todos = _query_files_to_process(nextToken)
        for todo in todos['data']['listFilesToProcess']['items']:
            image_sources.get(todo['sourceType']).append(todo)
        nextToken = todos['data']['listFilesToProcess']['nextToken']
    return image_sources
