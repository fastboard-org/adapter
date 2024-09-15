import pymongo
from bson.objectid import ObjectId


from cachetools import TLRUCache
import time

INACTIVITY_TIMEOUT = 60 * 5


class CustomCache(TLRUCache):
    def __delitem__(self, key):
        print(f"Removing {key} from cache")
        super().__delitem__(key)

    def expire(self, time=None):
        expired_items = list(super().expire(time))
        for key, _ in expired_items:
            print(f"Expiring {key} from cache")
        return expired_items


def custom_ttu(_key, _value, now):
    return now + INACTIVITY_TIMEOUT


cache = CustomCache(maxsize=20, ttu=custom_ttu, timer=time.monotonic)


def get_mongo_client(connection_string: str):
    if connection_string in cache:
        print(f"Cache hit for {connection_string}")
        return cache[connection_string]
    print(f"Cache miss for {connection_string}")
    client = pymongo.MongoClient(connection_string)
    cache[connection_string] = client
    return client


async def execute_query(
    connection_string: str,
    collection: str,
    method: str,
    filter_body: dict = None,
    update_body: dict = None,
):
    db = get_mongo_client(connection_string).get_database()[collection]

    if method == "aggregate":
        res = list(db.aggregate(pipeline=filter_body))
    elif method == "count":
        res = db.count_documents(filter_body)
    elif method == "distinct":
        res = db.distinct(filter_body)
    elif method == "find":
        res = list(db.find(filter_body))
    elif method == "findOne":
        res = db.find_one(filter_body)
    elif method == "findOneAndDelete":
        res = db.find_one_and_delete(filter_body)
    elif method == "findOneAndReplace":
        res = db.find_one_and_replace(filter_body, update_body)
    elif method == "findOneAndUpdate":
        res = db.find_one_and_update(filter_body, update_body)
    elif method == "insertOne":
        res = db.insert_one(filter_body).inserted_id
    elif method == "insertMany":
        res = db.insert_many(filter_body).inserted_ids
    elif method == "updateOne":
        modified_count = db.update_one(filter_body, update_body).modified_count
        res = {"modified_count": modified_count}
    elif method == "updateMany":
        modified_count = db.update_many(filter_body, update_body).modified_count
        res = {"modified_count": modified_count}
    elif method == "deleteOne":
        deleted_count = db.delete_one(filter_body).deleted_count
        res = {"deleted_count": deleted_count}
    elif method == "deleteMany":
        deleted_count = db.delete_many(filter_body).deleted_count
        res = {"deleted_count": deleted_count}

    if isinstance(res, ObjectId):
        res = str(res)

    if isinstance(res, dict):
        for k, v in res.items():
            if isinstance(v, ObjectId):
                res[k] = str(v)
    elif isinstance(res, list):
        for item in res:
            if isinstance(item, ObjectId):
                res[res.index(item)] = str(item)
            if isinstance(item, dict):
                for k, v in item.items():
                    if isinstance(v, ObjectId):
                        item[k] = str(v)

    return {"body": res}
