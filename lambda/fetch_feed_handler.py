import boto3
import os
import feedparser

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

def insertTable(table, items):
    with table.batch_writer() as writer:
        for item in items:
            writer.put_item(item)

def getFeedImage(feedDetail):
    imageUrl = None
    if "media_content" not in feedDetail :
        return imageUrl
    for media in feedDetail["media_content"]:
        if "medium" in media:
            if media["medium"] == "image":
                imageUrl = media["url"]
                break
    return imageUrl


def shapeFeed(feedOriginDetail, feedDetail):
    feedOrigin = feedOriginDetail["title"]
    return {
        "origin": feedOrigin,
        "title": feedDetail["title"],
        "link": feedDetail["link"],
        "author": feedDetail["author"],
        "published": feedDetail["published"],
        "imageURL": getFeedImage(feedDetail),
    }

def handler(event, context):
    feed_origin_table = dynamodb.Table(feed_origin_table_name)
    feed_item_table = dynamodb.Table(feed_item_table_name)

    result = scanTable(feed_origin_table)
    feedList = []
    for site in result:
        feed = feedparser.parse(site["siteURL"])
        feedOriginDetail = feed["feed"]
        feedEntries = feed["entries"]
        for feedDetail in feedEntries:
            feedList.append(shapeFeed(feedOriginDetail,feedDetail))
    
    insertTable(feed_item_table, feedList)

    return True