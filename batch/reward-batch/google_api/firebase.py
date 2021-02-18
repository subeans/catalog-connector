"""
firebase 에 쌓이는 analytics raw data 를 bigquery 로 가져오고 reward 계산을 하기위한 형식으로 바꾸는 함수 
"""
import pandas as pd 
import boto3
import json
from google.cloud import bigquery
from google.oauth2 import service_account
from auths import bigquery as auth

s3 = boto3.client('s3')

credentials = service_account.Credentials.from_service_account_info(auth.GOOGLE_CLIENT_CREDENTIALS)
client = bigquery.Client(credentials=credentials, project=credentials.project_id,)

def setting_bigquery():
    
    datasets = list(client.list_datasets())
    dataset_list = [dataset.dataset_id for dataset in datasets]
    dataset_name = dataset_list[0]

    project_id = client.project

    dataset = client.get_dataset(dataset_name)
    tables = list(client.list_tables(dataset)) 
    table_list=[] 
    if tables:
        for table in tables:
            table_list.append(table.table_id)
    
    return project_id, dataset_name , table_list


# firebase 에 쿼리를 날리고 결과를 json 으로 반환하는 함수 
def query_to_rawdata(project_id,dataset_name,table_name):
    
    query ="""
        select event_name,event_timestamp , (SELECT value.int_value FROM UNNEST(event_params)
        WHERE key = "product_id") AS product_id , (SELECT value.int_value FROM UNNEST(event_params)
        WHERE key = "product_index") AS product_index , (SELECT value.double_value FROM UNNEST(event_params)
        WHERE key = "page_id" ) AS page_id 
        from {0}.{1}.{2}
        where event_name = 'click_event' or event_name = 'impression_event'
        order by event_timestamp
        """.format(project_id,dataset_name,table_name)

    query_job = client.query(query)


    # API request - starts the query
    results = query_job.result() # Waits for job to complete.
    
    records = [dict(row) for row in results]
    
    return records



# 반환된 json 파일을 reward함수에서 계산할 수 있도록 
# 모든 데이터가 섞인 json에서 필요한 product_id 와 click log 반환하는 함수 
def preprocess(input_data,N):
    data = pd.DataFrame(input_data)

    sort_columns = 'page_id'
    data = data.sort_values(sort_columns)
    
    page_ids = list(data['page_id'].value_counts().index)
    
    all_log = []
    
    for page_id in page_ids:
        products_id = [0 for _ in range(N)]
        click_log = [0 for _ in range(N)]
        
        impression_condition = (data['page_id'] == page_id ) & (data['event_name'] =='impression_event') 
        impression_data = data[impression_condition]
        
        click_condition = (data['page_id'] == page_id ) & (data['event_name'] =='click_event') 
        click_data = data[click_condition]

        # 보여진 상품의 위치를 찾기
        for i in range(len(impression_data)):
            index=impression_data.iloc[i]['product_index']
            products_id[index] = str(impression_data.iloc[i]['product_id'])
    
        for i in range(len(click_data)):
            index = click_data.iloc[i]['product_index']
            click_log[index] = 1 
        info = {
            "products_id":products_id,
            "click_log":click_log
        }
        all_log.append(info)

    return all_log
