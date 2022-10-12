import json
import boto3
import os

feed_origin_table_name = os.environ['RSS_ORIGIN_TABLE']
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
    feed_origin_table = dynamodb.Table(feed_origin_table_name)
    feed_item_table = dynamodb.Table(feed_item_table_name)

    result = scanTable(feed_origin_table)
    print (feed_item_table_name)
    print (result)

    return result