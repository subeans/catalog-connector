from facebook_api import setting
import os 
import sys


def upload(name,catalog_id):
    not_saved_set = setting.facebook_catalog_to_mongodb(name,catalog_id,os.environ['FACEBOOK_TOKEN'])
    return {"request again ":not_saved_set}


def main(argv):
    collection_name = argv[1]
    catalog_id = argv[2]

    again_set_list = upload(collection_name,catalog_id)
    return again_set_list


if __name__ == "__main__":
    again = main(sys.argv)
