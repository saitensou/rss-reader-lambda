import aws_cdk as cdk
import aws_cdk.aws_dynamodb as DynamoDB
import aws_cdk.aws_lambda as Lambda
import aws_cdk.aws_logs as Logs
import aws_cdk.aws_apigateway as APIgateway
import aws_cdk.aws_events as Events
import aws_cdk.aws_events_targets as EventTargets
from constructs import Construct


class CdkStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # tables
        rss_origin_table = DynamoDB.Table(
            self,
            "rss_origin_table",
            table_name="rss_origin_table",
            partition_key=DynamoDB.Attribute(
                name="siteURL", type=DynamoDB.AttributeType.STRING
            ),
            sort_key=DynamoDB.Attribute(
                name="siteName", type=DynamoDB.AttributeType.STRING
            ),
            billing_mode=DynamoDB.BillingMode.PAY_PER_REQUEST,
        )

        rss_feed_item_table = DynamoDB.Table(
            self,
            "rss_feed_item_table",
            table_name="rss_feed_item_table",
            partition_key=DynamoDB.Attribute(
                name="link", type=DynamoDB.AttributeType.STRING
            ),
            sort_key=DynamoDB.Attribute(
                name="published", type=DynamoDB.AttributeType.STRING
            ),
            billing_mode=DynamoDB.BillingMode.PAY_PER_REQUEST,
        )

        # layers
        feedparser_layer = Lambda.LayerVersion(
            self,
            "feedparser_layer",
            removal_policy=cdk.RemovalPolicy.RETAIN,
            code=Lambda.Code.from_asset("lambda-layer"),
            compatible_runtimes=[Lambda.Runtime.PYTHON_3_9],
        )

        # functions
        rss_fetch_lambda = Lambda.Function(
            self,
            "rss_fetch_lambda",
            runtime=Lambda.Runtime.PYTHON_3_9,
            function_name="rss_fetch_lambda",
            code=Lambda.Code.from_asset("lambda"),
            handler="fetch_feed_handler.handler",
            log_retention=Logs.RetentionDays.ONE_WEEK,
            timeout=cdk.Duration.minutes(5),
            environment={
                "RSS_ORIGIN_TABLE": rss_origin_table.table_name,
                "RSS_FEED_ITEM_TABLE": rss_feed_item_table.table_name,
            },
            layers=[feedparser_layer],
        )
        rss_origin_table.grant_read_data(rss_fetch_lambda)
        rss_feed_item_table.grant_read_write_data(rss_fetch_lambda)

        rss_serve_lambda = Lambda.Function(
            self,
            "rss_serve_lambda",
            runtime=Lambda.Runtime.PYTHON_3_9,
            function_name="rss_serve_lambda",
            code=Lambda.Code.from_asset("lambda"),
            handler="serve_feed_handler.handler",
            log_retention=Logs.RetentionDays.ONE_WEEK,
            timeout=cdk.Duration.seconds(10),
            environment={"RSS_FEED_ITEM_TABLE": rss_feed_item_table.table_name},
        )
        rss_feed_item_table.grant_read_data(rss_serve_lambda)

        # API gateway
        saitensou_rss_api_service = APIgateway.LambdaRestApi(
            self,
            "saitensou_rss_api_service",
            handler=rss_serve_lambda,
            proxy=False,
            rest_api_name="saitensou_rss_api_service",
        )
        saitensou_api_get_rss = saitensou_rss_api_service.root.add_resource("rss")
        saitensou_api_get_rss.add_method("GET")

        # corn job - everyday 2pm
        saitensou_fetch_rss_cron = Events.Rule(
            self,
            "saitensou_fetch_rss_cron",
            schedule=Events.Schedule.cron(hour="14", minute="0"),
            targets=[EventTargets.LambdaFunction(handler=rss_fetch_lambda)],
        )
