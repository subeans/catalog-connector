import pymongo

MONGODB_USER = 'digester_prod'
MONGODB_PASSWORD = 'qmfforvldzm'
MONGODB_URI = 'mongodb://%s:%s@3.34.3.239:27017' % (MONGODB_USER, MONGODB_PASSWORD)
MONGODB_DATABASE = 'prod'

mongo_uri = MONGODB_URI
mongo_db = MONGODB_DATABASE
client = pymongo.MongoClient(mongo_uri)
db = client[mongo_db]

def simple_reward(click_count,N):
    per_rewards=[0 for _ in range(N)]
    reward=N
    for i in range(N):
        if click_count[i]==1:
            per_rewards[i]=reward
    return per_rewards

# 상품을 슬라이드 형식으로 보여줄 때 상품 위치를 고려한 reward 계산 
def distance_reward(click_count,N):
    per_rewards=[0 for _ in range(N)]
    reward = N
    distance_reward=[0 for _ in range(N)]

    #click 된 상품의 reward 구하기 
    for i in range(N):
        if click_count[i]!=0:
            per_rewards[i]=reward
            reward-=1
        
    # click 안된 상품 reward 구하기
    penalty_reward=0
    for i in range(N-1,-1,-1):
        if per_rewards[i]==0:
            # 해당 상품 다음으로 click 을 한 상품에 대한 패널티를 다 받는 것  
            for j in range(N-1,i,-1):
                if per_rewards[j]!=0:
                    penalty_reward=distance_reward[j]
                    distance_reward[i]+=(penalty_reward*-(j-i))
        else :
            penalty_reward=per_rewards[i]
            distance_reward[i]=per_rewards[i]
            
    return distance_reward

def reward_to_mongo(name,reward,pick_items_id,N):
    collection = db[name]

    for i in range(N):
        item=list(collection.find({'product_id':pick_items_id[i]}))
        
        old_reward=item[0]['product_reward']
        old_click = item[0]['product_click_count']
        impressioned = item[0]['product_impression_count']
        item_id=item[0]['product_id']
        
        update_reward = old_reward+reward[i]

        # reward 변화가 있으면 click + , impression + 
        if old_reward != update_reward:
            
            collection.update_many(
                {
                "product_id":item_id,
                },
                {
                '$set':{
                'product_reward': update_reward,
                'product_click_count': old_click+1 ,
                'product_impression_count' : impressioned+1
                }
            }
        )

        else:
            collection.update_many(
                {
                "product_id":item_id,
                },
                {
                '$set':{
                'product_impression_count': impressioned+1
                    }
                }
            )
