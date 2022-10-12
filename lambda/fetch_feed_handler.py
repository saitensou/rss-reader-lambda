from dateutil.parser import parse
import boto3
import os
import feedparser
from datetime import datetime
import dateutil.relativedelta

feed_origin_table_name = os.environ["RSS_ORIGIN_TABLE"]
feed_item_table_name = os.environ["RSS_FEED_ITEM_TABLE"]
dynamodb = boto3.resource("dynamodb")
month_delta = -3
max_persite = 25
threadshold = datetime.now() + dateutil.relativedelta.relativedelta(months=month_delta)


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


def getPublished(feedDetail):
    if "published" in feedDetail:
        return feedDetail["published"]
    if "pubDate" in feedDetail:
        return feedDetail["pubDate"]
    if "updated" in feedDetail:
        return feedDetail["updated"]
    return None


def getLink(feedDetail):
    if "link" in feedDetail:
        return feedDetail["link"]
    return None


def getTitle(feedDetail):
    if "title" in feedDetail:
        return feedDetail["title"]
    return None


def shapeFeed(siteName, feedDetail):
    return {
        "origin": siteName,
        "author": feedDetail["author"] if "author" in feedDetail else None,
        "title": getTitle(feedDetail),
        "link": getLink(feedDetail),
        "published": getPublished(feedDetail),
        "imageURL": getFeedImage(feedDetail),
    }


def appendFeed(feedList, feedItem):
    if "link" in feedItem and "published" in feedItem:
        try:
            published = parse(feedItem["published"]).replace(tzinfo=None)
            if published > threadshold:
                feedItem["published"] = published.strftime("%d/%m/%Y")
                feedList.append(feedItem)
        except Exception as e:
            print(e)
            return


def handler(event, context):
    feed_origin_table = dynamodb.Table(feed_origin_table_name)
    feed_item_table = dynamodb.Table(feed_item_table_name)

    scanResult = scanTable(feed_origin_table)
    feedList = []
    for site in scanResult:
        feed = feedparser.parse(site["siteURL"])
        feedEntries = feed["entries"]
        count = 0
        for feedDetail in feedEntries:
            appendFeed(feedList, shapeFeed(site["siteName"], feedDetail))
            count += 1
            if count >= max_persite:
                break

    print(len(feedList))
    insertTable(feed_item_table, feedList)
    print("insert table success")

    return len(feedList)