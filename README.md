# RSS reader lambda

This project tries to perform an aggregrations towards several RSS feeds on AWS

It includes following things:
- 2 dynamodb table
    - feed origin table
    - feed item table
- 2 Lambda functions
    - Fetching lambda
        - triggered by cron job
        - index the feeds from origin and put to feed item
    - Serving lambda
        - triggered by API gateway
        - return the list of feed items in dynamodb

