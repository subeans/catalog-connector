from google_api import firebase
from utilities import rewards
import os 
import sys



def ranking_process(name,reward_option,period,N):
    project_id , dataset_name, table_list = firebase.setting_bigquery()
    idx = len(table_list)-1 
    for day in range(idx,idx-period,-1):
        table_name = table_list[day]
        data = firebase.query_to_rawdata(project_id,dataset_name,table_name)
        log_info = firebase.preprocess(data,N)
    
        for i in range(len(log_info)):

            if reward_option=="simple":
                reward = rewards.simple_reward(log_info[i]['click_log'],N)
            else:
                reward = rewards.distance_reward(log_info[i]['click_log'],N)
        
            try:
                rewards.reward_to_mongo(name,reward,log_info[i]['products_id'],N)
            except:
                continue

def main(argv):
    collection_name = argv[1]
    reward_option = argv[2]
    period = int(argv[3])
    N = 3
    ranking_process(collection_name,reward_option,period,N)


if __name__ == "__main__":
    main(sys.argv)
