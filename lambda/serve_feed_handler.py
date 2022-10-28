import json
import boto3
import os
import urllib.parse

feed_item_table_name = os.environ["RSS_FEED_ITEM_TABLE"]
dynamodb = boto3.resource("dynamodb")


def scanTable(table, lastKey):
    response = None
    if lastKey is None:
        response = table.scan(Limit=25)
    else:
        response = table.scan(Limit=25, ExclusiveStartKey=lastKey)
    data = response["Items"]
    nextkey = response["LastEvaluatedKey"]
    return (data, nextkey)


def handler(event, context):
    feed_item_table = dynamodb.Table(feed_item_table_name)

    lastKey = None
    if "queryStringParameters" in event and event["queryStringParameters"] is not None :
        if "lastKey" in event["queryStringParameters"]:
            lastKey_str = urllib.parse.unquote_plus(event["queryStringParameters"]["lastKey"])
            print(lastKey_str)
            lastKey = json.loads(lastKey_str)
            print(lastKey)
    
    print("Start scan")

    (data, nextkey) = scanTable(feed_item_table, lastKey)
    print(data)
    nextkey_json = json.dumps(nextkey)
    print(nextkey_json)
    result = {
        "data": data,
        "nextkey": urllib.parse.quote_plus(nextkey_json),
    }
    json_result = json.dumps(result)
    print(json_result)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json_result,
    }
