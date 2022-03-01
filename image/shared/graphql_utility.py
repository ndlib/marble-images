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


def _mutate_item(item_id: str, height: int, width: int) -> dict:
    """ updates items last modified date, height, and width """
    operation = """
        mutation saveFileLastProcessedDate($id: String!, $height: Int, $width: Int) {
            saveFileLastProcessedDate(itemId: $id,  height: $height, width: $width) {
                id
                modifiedDate
                dateLastProcessed
            }
        }"""
    operation_name = "saveFileLastProcessedDate"
    variables = {"id": item_id, "height": height, "width": width}
    return graphql.run_operation(operation, operation_name, variables)


def _remove_item(item_id: str) -> dict:
    """ removes an item based on item_id """
    operation = """
        mutation removeItemToProcess($itemId: String!) {
            removeItemToProcess(itemId: $itemId) {
                recordsDeleted
            }
        }"""
    operation_name = "removeItemToProcess"
    variables = {"itemId": item_id}
    return graphql.run_operation(operation, operation_name, variables)


def update_item(item_id: str, height: int, width: int) -> None:
    return _mutate_item(item_id, height, width)


def remove_missing_item(item_id: str) -> None:
    return _remove_item(item_id)


def generate_image_lists():
    todos = _query_files_to_process()
    img_data = todos['data']['listFilesToProcess']['items']
    nextToken = todos['data']['listFilesToProcess']['nextToken']
    while nextToken:
        todos = _query_files_to_process(nextToken)
        img_data.extend(todos['data']['listFilesToProcess']['items'])
        nextToken = todos['data']['listFilesToProcess']['nextToken']
    return img_data
