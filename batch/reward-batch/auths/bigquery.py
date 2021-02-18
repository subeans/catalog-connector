import boto3
import json


AWS_ACCESS_KEY_ID = 'AKIAQECLFED6JTMTPPIS'
AWS_SECRET_ACCESS_KEY = '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'

s3 = boto3.client('s3',
                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                  region_name='ap-northeast-2')

# Google APIs Auth
GOOGLE_CLIENT_CREDENTIALS = json.loads(
    s3.get_object( Bucket='catalog-connector', 
    Key='iamstudio-firebase-d2ff6e03fd6e.json')['Body'].read().decode())
