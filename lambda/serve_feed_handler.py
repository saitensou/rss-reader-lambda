import json
import boto3
import os

feed_item_table_name = os.environ["RSS_FEED_ITEM_TABLE"]
dynamodb = boto3.resource("dynamodb")


def scanTable(table):
    response = table.scan()
    data = response["Items"]

    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        data.extend(response["Items"])

    return data


def handler(event, context):
    feed_item_table = dynamodb.Table(feed_item_table_name)

    result = scanTable(feed_item_table)
    json_result = json.dumps(result)
    print(json_result)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json_result,
    }
