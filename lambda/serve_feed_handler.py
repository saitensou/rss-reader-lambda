import json
import boto3
import os

feed_item_table_name = os.environ["RSS_FEED_ITEM_TABLE"]
dynamodb = boto3.resource("dynamodb")


def scanTable(table, lastKey):
    response = None
    if lastKey is None:
        response = table.scan(Limit=25, ExclusiveStartKey=response["LastEvaluatedKey"])
    else:
        response = table.scan(Limit=25)
    data = response["Items"]
    nextkey = response["LastEvaluatedKey"]
    return (data, nextkey)


def handler(event, context):
    feed_item_table = dynamodb.Table(feed_item_table_name)

    lastKey = None
    if lastKey in event["queryStringParameters"]:
        lastKey = event["queryStringParameters"]["lastKey"]

    data, nextkey = scanTable(feed_item_table, lastKey)
    result = {
        "data": data,
        "nextkey": nextkey,
    }
    json_result = json.dumps(result)
    print(json_result)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json_result,
    }
