# push to dynamodb (appened `assets` folder)
aws dynamodb batch-write-item \
    --request-items "file://$(pwd)/assets/rss.json" \
    --region ap-northeast-1 \
    --profile [PROFILE] 

# try pagination
aws dynamodb scan \
    --table-name rss_feed_item_table \
    --limit 2 \
    --region ap-northeast-1 \
    --profile [PROFILE]