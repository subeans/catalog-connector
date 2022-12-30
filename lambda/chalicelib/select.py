"""

N 개 선택하는 방법

select_act : 조건에 맞는 select 실행 
cold_act : click log , impression log 둘다 충분하지 않을 때 
partial_act : impression log 는 쌓여있고 click log 가 충분하지 않을 때 부분적으로 랜덤하게 뽑는 과정 
warm_act : click log , impression log 가 충분할 때 reward 를 기준으로 ranking 과정을 거쳐 상품을 뽑는 과정 

"""


import random
import pymongo
import json
from bson import json_util

MONGODB_USER = ''
MONGODB_PASSWORD = ''
MONGODB_URI = 'mongodb://%s:%s@3.34.3.239:27017' % (MONGODB_USER, MONGODB_PASSWORD)
MONGODB_DATABASE = 'prod'

mongo_uri = MONGODB_URI
mongo_db = MONGODB_DATABASE
client = pymongo.MongoClient(mongo_uri)
db = client[mongo_db]


def select_act(name,N,pick_option):
    col = db[name]

    if pick_option == 'all':
        count = col.find().count()
        non_impressioned_count=col.find({'product_impression_count':0}).count()
        non_clicked_count=col.find({'product_click_count':0}).count()

    else:
        count = col.find({'catalog_set_id':pick_option}).count()
        non_impressioned_count=col.find({'product_impression_count':0,'catalog_set_id':pick_option}).count()
        non_clicked_count=col.find({'product_click_count':0,'catalog_set_id':pick_option}).count()

    acted=''

    # cold start , partial start , warm start 기준 나눌 standard_count
    # count 는 전체 상품의 개수 
    standard_count = count*1/4

    # 전체 상품의 1/4도 아직 user 에게 보여주지 않았다면 cold start 
    if non_impressioned_count > standard_count:
        # id list 반환 
        impression = cold_act(name,N,pick_option)
        acted='Cold start : random in total items 3 '

    # impression 된 상품은 기준 이상이나, click 된 상품이 기준 이하인 경우 
    # 1개는 top reward product ,N-1은 전체 상품에서 random 
    elif non_clicked_count > standard_count :
        impression=partial_act(name,N,pick_option)
        acted='Partial start : reward Top 1 + random in total items 2'

    # 1개는 top reward product , N-1 은 reward가 양수인 상품에서 random 
    else:
        impression = warm_act(name,N,pick_option)
        acted='Warm start : reward Top1 + random in positive_reward 2'
    
    impression = parse_json(impression)

    return  {"how":acted,"result":impression} 

def parse_json(data):
    return json.loads(json_util.dumps(data))

def cold_act(name,N,pick_option):

    col = db[name]
    # item 전체를 섞고 N 개 뽑기

    if pick_option == 'all':
        random_items = col.aggregate([{'$sample':{'size':N}}])
    else:
        random_items = col.aggregate([{'$match':{'catalog_set_id' : pick_option}},{'$sample':{'size':N}}])

    pick_items = [ items for items in random_items]

    return pick_items

def partial_act(name,N,pick_option):
    col = db[name]
    # pick_items_id=[]        
    pick_items=[]
    # 전체 N개 중에 1개는 reward 가장 큰 상품 하나 고르고 
    sorting=col.find().sort("product_reward",-1)
    top_item=sorting[:1]


    for x in top_item:
        pick_items.append(x)

    # 나머지 N-1 개는 전체 상품에서(지정한 set가 있다면 지정 세트 내에서) 랜덤으로 2개 뽑는다
    if pick_option == 'all':
        random_items = col.aggregate([{'$sample':{'size':N-1}}])
    else:
        random_items = col.aggregate([{'$match':{'catalog_set_id' : pick_option}},{'$sample':{'size':N-1}}])
    

    random_items = [ items for items in random_items]
    random_items.sort(key=lambda random_items:random_items['product_reward'],reverse=True)


    for i in range(N-1):
        pick_items.append(random_items[i])


    return pick_items


def warm_act(name,N,pick_option):
    col = db[name]
    pick_items=[]   

    if pick_option=='all':
        sorting=col.find().sort("product_reward",-1)
    else :
        sorting=col.find({'catalog_set_id':pick_option}).sort("product_reward",-1)
    
    # top reward product 가져오기 
    top_item=sorting[:1]

    for x in top_item:
        pick_items.append(x)
    
    # 0 ( standard_reward ) 보다 큰 reward 를 갖는 product 의 평균
    average_reward = calc_average_reward(name,0,pick_option)

    if pick_option == "all":
        random_items = col.aggregate([{'$match':{'product_reward':{'$gt':average_reward } }},{'$sample':{'size':N-1}}])
    else:
        random_items = col.aggregate([{'$match':{'catalog_set_id' : pick_option ,'product_reward':{'$gt':average_reward } }},{'$sample':{'size':N-1}}])

    pick_random_standard_items = [ items for items in random_items]
    pick_random_standard_items.sort(key=lambda pick_random_standard_items:pick_random_standard_items['product_reward'],reverse=True)
    
    print(len(pick_random_standard_items))
    for i in range(N-1):
        pick_items.append(pick_random_standard_items[i])
    return pick_items

def calc_average_reward(name,standard_reward ,pick_option):
    col = db[name]

    if pick_option == 'all':
        positive_reward_products = col.find({'product_reward':{'$gt':standard_reward} })
        positive_reward_products_count = col.find({'product_reward':{'$gt':standard_reward} }).count()
    else:
        positive_reward_products = col.find({'product_reward':{'$gt':standard_reward} ,'catalog_set_id':pick_option})
        positive_reward_products_count = col.find({'product_reward':{'$gt':standard_reward} ,'catalog_set_id':pick_option}).count()
    
    reward_sum=0

    for item in positive_reward_products :
        reward_sum+=item['product_reward']

    try:
        average_reward = reward_sum//positive_reward_products_count
    except:
        average_reward = -1
    return average_reward 


