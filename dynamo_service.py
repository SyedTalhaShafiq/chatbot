import boto3
import uuid
import time
import os
import logging
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("TML-DynamoDB")

AWS_REGION = os.getenv("AWS_REGION", "eu-north-1") 
TABLE_NAME = "TML_Chat_History"

def get_table():
    """
    Initializes the connection to the DynamoDB Table.
    """
    try:
        dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        return dynamodb.Table(TABLE_NAME)
    except Exception as e:
        logger.error(f"Failed to connect to DynamoDB: {e}")
        return None

def save_chat_log(email: str, query: str, response: str, status: str = "success"):
    """
    Saves a single chat interaction to DynamoDB.
    """
    table = get_table()
    if not table:
        return

    timestamp = int(time.time()) 
    readable_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
    
    item = {
        'Email': email,            # PARTITION KEY
        'Timestamp': timestamp,    # SORT KEY
        'LogID': str(uuid.uuid4()),
        'Query': query,
        'Response': response,
        'Status': status,
        'DateReadable': readable_time
    }

    try:
        table.put_item(Item=item)
        logger.info(f"[-] Log saved for {email} | Status: {status}")
    except ClientError as e:
        logger.error(f"[!] DynamoDB Write Error: {e.response['Error']['Message']}")

def get_user_history(email: str):
    table = get_table()
    try:
        from boto3.dynamodb.conditions import Key
        response = table.query(
            KeyConditionExpression=Key('Email').eq(email)
        )
        return response['Items']
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        return []