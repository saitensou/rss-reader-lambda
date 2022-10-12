# push to dynamodb (appened `assets` folder)
aws dynamodb batch-write-item --request-items "file://$(pwd)/assets/rss.json" --region ap-northeast-1 --profile [PROFILE] 