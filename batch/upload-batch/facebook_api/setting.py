'''
Facebook graph api 를 사용해서 facebook catalog 내 상품을 mongodb 로 저장하는 과정 
'''
import requests 
import json
import pymongo


MONGODB_USER = 'digester_prod'
MONGODB_PASSWORD = 'qmfforvldzm'
MONGODB_URI = 'mongodb://%s:%s@3.34.3.239:27017' % (MONGODB_USER, MONGODB_PASSWORD)
MONGODB_DATABASE = 'prod'


mongo_uri = MONGODB_URI
mongo_db = MONGODB_DATABASE
client = pymongo.MongoClient(mongo_uri)
db = client[mongo_db]

def facebook_catalog_to_mongodb(name,catalog_id,token):

    catalog_sets_id  = find_sets(catalog_id,token)
    bad_set_list=[]
    paging_count = 1000
    # set 가 여러개 있을 때 
    try:
        for i in range (len(catalog_sets_id)):
            set_id = catalog_sets_id[i]
            
            set_items= find_products(set_id,paging_count,token)

            # api call error 나면 upload_mongo 진행할때 error 남 
            try:
                upload_mongo(name,set_id,set_items,0)
            except:
                bad_set_list.append(set_id)
                print("Facebook API call Error")

    # set 하나인 경우 
    except:
        all_products = find_products(catalog_id,paging_count,token)
        upload_mongo(name,catalog_id,all_products,0)


    return bad_set_list



def find_sets(catalog_id , token):
    URL = "https://graph.facebook.com/v9.0/{catalog_id}/product_sets".format(catalog_id=catalog_id)

    params = {
        'fields':"['product_count','id','name']",
        'access_token' :token
    }

    response = requests.request('GET',URL,params=params) 

    text=response.text
    product_text=json.loads(text)
    sets=product_text['data']

    sets_id = [sets[i]['id'] for i in range(len(sets))]

    # sets_list : 하나의 카탈로그 내에 있는 set id 리스트 
    return sets_id 

def find_products(set_id,N,token):
    now_URL = "https://graph.facebook.com/v9.0/{set_id}/products".format(set_id=set_id)

    params = {
        'fields':"['product_count','availability','brand','condition','id','image_url','name','price']",
        'access_token' :token,
        'limit':N
    }
    
    next_URL = ""
    set_all_items=[]

    while(1):
        response = requests.request('GET',now_URL,params=params) 
        if response.status_code >= 400:
            return {'status_code':response.status_code , 'message':'Facebook API Error during find products','num':len(set_all_items)} 
        text=response.text
        product_text=json.loads(text)

        # paging 의  next를 이용하여 다음 product 목록을 불러오다가 더 이상 다음장이 없으면 paging next 가 없음 
        # 그때 break
        try:
            next_URL = product_text['paging']['next']
            # paging 정보가 뜨지만 마지막 페이지에 대한 url 을 계속 나타낼 때 
            if now_URL == next_URL : break
        except:
            break
        
        if len(product_text['data'])!=0:
            set_all_items.append(product_text['data'])
        
        now_URL = next_URL

    set_all_items = sum(set_all_items,[])
    # set_all_items : 하나의 세트 안에 들어있는 모든 상품이 있는 리스트 
    return set_all_items

def upload_mongo(name,set_id,set_data,weight):
    col = db[name]
    col.create_index('product_id')
    col.create_index('catalog_set_id')
    #한번에 업로드할 아이템 수집하는 리스트 
    upload_items=[]

    for i in range(len(set_data)):
        # 이미 product 가 DB에 저장된 상태라면 
        # 하나의 상품이 여러 set 에 포함되어 set id 가 여러개인 경우 
        if col.find({'product_id':set_data[i]['id']}).count() !=0 : 
            # set id 리스트가 안에 지금 set_id 가 있는지 없는지 확인 
            if col.find({'catalog_set_id':set_id , 'product_id':set_data[i]['id']}).count()!=0:
                continue
            else:
             col.update( 
                    { 'product_id' : set_data[i]['id'] },
                    { '$push' : {'catalog_set_id' : set_id} }
                )
        else :  
            info = {
                'product_id':set_data[i]['id'],
                'catalog_set_id':[set_id],
                'product_info':set_data[i],
                'product_reward':weight,
                'product_click_count':0,
                'product_impression_count':0
            }
            upload_items.append(info)

    if len(upload_items)!=0:
        col.insert_many(upload_items)


'''
그 외 mongodb 에 쌓인 product reward 확인하는 check_rank 
쌓인 product reward 값 리셋하는 reset 
'''
def check_rank(name):
    col = db[name]

    product_info = []

    sorting=col.find().sort("product_reward",-1)
    sorted_top100 = sorting[:100]
    for items in sorted_top100:
        info = {
            'product_id':items['product_id'],
            'product_reward':items['product_reward'],
            'product_click_count':items['product_click_count'],
            'product_impression_count':items['product_impression_count']
        }
        product_info.append(info)

    return product_info

def reset(name):
    #mongodb 값 reset 
    col = db[name]

    products=col.find()

    for product in products:
        col.update_many(
                {
                "product_id":product['product_id'],
                },
                {
                '$set':{
                'product_reward': 0,
                'product_click_count': 0 ,
                'product_impression_count' : 0
                }
            }
        )