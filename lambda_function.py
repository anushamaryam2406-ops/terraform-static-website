# ...existing code...
import os
import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table_name = os.environ.get("TABLE_NAME", "visitor-count")
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    try:
        response = table.update_item(
            Key={"id": "main"},
            UpdateExpression="ADD visit_count :inc",
            ExpressionAttributeValues={":inc": 1},
            ReturnValues="UPDATED_NEW"
        )

        attrs = response.get("Attributes", {})
        raw = attrs.get("visit_count", 0)

        try:
            count = int(raw)
        except Exception:
            count = int(Decimal(str(raw)))

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": json.dumps({"visits": count})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": json.dumps({"error": str(e)})
        }
# ...existing code...