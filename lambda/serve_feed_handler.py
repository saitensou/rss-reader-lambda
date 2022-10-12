import boto3
import os

feed_item_table_name = os.environ['RSS_FEED_ITEM_TABLE']
dynamodb = boto3.resource('dynamodb')

def scanTable(table):
    response = table.scan()
    data = response['Items']

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        data.extend(response['Items'])
    
    return data


def handler(event, context):
    feed_item_table = dynamodb.Table(feed_item_table_name)

    result = scanTable(feed_item_table)
    print(result)

    return result