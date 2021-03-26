from . import graphql


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
    todos = _query_files_to_process()
    img_data = todos['data']['listFilesToProcess']['items']
    nextToken = todos['data']['listFilesToProcess']['nextToken']
    while nextToken:
        todos = _query_files_to_process(nextToken)
        img_data.extend(todos['data']['listFilesToProcess']['items'])
        nextToken = todos['data']['listFilesToProcess']['nextToken']
    return img_data
