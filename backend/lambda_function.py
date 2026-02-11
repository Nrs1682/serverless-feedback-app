import json
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('FeedbackTable')

HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type"
}

def lambda_handler(event, context):

    path = event.get("rawPath", "")
    method = event["requestContext"]["http"]["method"]

    # Normalize stage path
    path = path.replace("/production", "")

    # --- HANDLE CORS PREFLIGHT ---
    if method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": HEADERS,
            "body": ""
        }

    # POST /feedback
    if path == "/feedback" and method == "POST":
        body = json.loads(event["body"])

        item = {
            "feedbackId": str(uuid.uuid4()),
            "name": body.get("name"),
            "email": body.get("email"),
            "message": body.get("message"),
            "createdAt": datetime.utcnow().isoformat()
        }

        table.put_item(Item=item)

        return {
            "statusCode": 200,
            "headers": HEADERS,
            "body": json.dumps({"message": "Feedback submitted successfully"})
        }

    # GET /admin/feedback
    elif path == "/admin/feedback" and method == "GET":
        response = table.scan()

        items = sorted(
            response["Items"],
            key=lambda x: x["createdAt"],
            reverse=True
        )[:20]

        return {
            "statusCode": 200,
            "headers": HEADERS,
            "body": json.dumps(items)
        }

    return {
        "statusCode": 404,
        "headers": HEADERS,
        "body": json.dumps({"error": f"Not Found: {path}"})
    }
