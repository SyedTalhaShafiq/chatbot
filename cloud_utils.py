import boto3
import os
import zipfile
import shutil
import logging
import config
from botocore.exceptions import ClientError

logger = logging.getLogger("TML-CloudUtils")

def download_index_from_s3():
    """
    Downloads chroma_db.zip from S3 and extracts it to data/index.
    """
    s3 = boto3.client('s3', region_name=os.getenv("AWS_REGION", "eu-north-1"))
    
    local_zip_path = os.path.join(config.DATA_DIR, config.INDEX_ZIP_NAME)
    
    logger.info(f"[-] Connecting to S3 Bucket: {config.ARTIFACT_BUCKET}")
    
    try:
        if os.path.exists(config.INDEX_DIR):
            logger.info(f"[-] Removing old index at {config.INDEX_DIR}...")
            shutil.rmtree(config.INDEX_DIR)
        
        os.makedirs(config.DATA_DIR, exist_ok=True)

        logger.info(f"[-] Downloading {config.INDEX_ZIP_NAME}...")
        s3.download_file(config.ARTIFACT_BUCKET, config.INDEX_ZIP_NAME, local_zip_path)
        
        logger.info("[-] Extracting zip file...")
        with zipfile.ZipFile(local_zip_path, 'r') as zip_ref:
            zip_ref.extractall(config.DATA_DIR)
            
        logger.info("[SUCCESS] Vector DB updated from Cloud.")
        
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            logger.error("[!] Artifact not found in S3. Please upload chroma_db.zip first.")
        elif e.response['Error']['Code'] == "403":
            logger.error("[!] Access Denied. Check your AWS keys.")
        else:
            logger.error(f"[!] AWS Error: {e}")
    except Exception as e:
        logger.error(f"[!] Critical Error during S3 sync: {e}")
    finally:
        if os.path.exists(local_zip_path):
            os.remove(local_zip_path)