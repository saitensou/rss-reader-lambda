from dateutil.parser import parse
import boto3
import os
import feedparser
import json
import dateutil.relativedelta
import datetime

feed_origin_table_name = os.environ["RSS_ORIGIN_TABLE"]
feed_item_table_name = os.environ["RSS_FEED_ITEM_TABLE"]
dynamodb = boto3.resource("dynamodb")
month_delta = -3
max_persite = 25
threadshold = datetime.datetime.now() + dateutil.relativedelta.relativedelta(
    months=month_delta
)


def scanTable(table):
    response = table.scan()
    data = response["Items"]

    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        data.extend(response["Items"])

    return data


def insertTable(table, items):
    with table.batch_writer(overwrite_by_pkeys=["link", "published"]) as writer:
        for item in items:
            writer.put_item(item)


def getFeedImage(feedDetail):
    imageUrl = None
    if "media_content" not in feedDetail:
        return imageUrl
    for media in feedDetail["media_content"]:
        if "medium" in media:
            if media["medium"] == "image":
                imageUrl = media["url"]
                break
    return imageUrl


def shapeFeed(feedOriginDetail, feedDetail):
    return {
        "origin": feedOriginDetail["title"] if "title" in feedOriginDetail else None,
        "title": feedDetail["title"] if "title" in feedDetail else None,
        "link": feedDetail["link"] if "link" in feedDetail else None,
        "author": feedDetail["author"] if "author" in feedDetail else None,
        "published": feedDetail["published"] if "published" in feedDetail else None,
        "imageURL": getFeedImage(feedDetail),
    }


def appendFeed(feedList, feedItem):
    if "link" in feedItem and "published" in feedItem:
        try:
            published = parse(feedItem["published"]).replace(tzinfo=None)
            if published > threadshold:
                feedList.append(feedItem)
        except:
            return


def handler(event, context):
    feed_origin_table = dynamodb.Table(feed_origin_table_name)
    feed_item_table = dynamodb.Table(feed_item_table_name)

    scanResult = scanTable(feed_origin_table)
    feedList = []
    for site in scanResult:
        feed = feedparser.parse(site["siteURL"])
        feedOriginDetail = feed["feed"]
        feedEntries = feed["entries"]
        count = 0
        for feedDetail in feedEntries:
            appendFeed(feedList, shapeFeed(feedOriginDetail, feedDetail))
            count += 1
            if count >= max_persite:
                break

    print(len(feedList))
    print(json.dumps(feedList))

    insertTable(feed_item_table, feedList)

    return True
