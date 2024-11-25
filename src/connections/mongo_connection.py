import pymongo
from pymongo import UpdateOne
from bson.objectid import ObjectId

from cachetools import TLRUCache
import time
from connections.api_request import make_request
from bson import Decimal128
from lib.object_id import replace_objectid_strings

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

    return parse_response(res)


async def get_embeddings(query: str, api_key: str):
    url = "https://api.openai.com/v1/embeddings"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    response = await make_request(
        url, headers, "POST", {"input": query, "model": "text-embedding-ada-002"}
    )
    return response


async def bulk_update(connection_string: str, collection: str, updates: dict):
    db = get_mongo_client(connection_string).get_database()[collection]
    operations = []
    for id, update in updates.items():
        id = replace_objectid_strings(id)
        operations.append(UpdateOne({"_id": id}, {"$set": {"embedding": update}}))
    res = {"data": db.bulk_write(operations).bulk_api_result}
    return res


async def execute_vector_search(
    connection_string: str,
    api_key: str,
    collection: str,
    query: str,
    limit: int,
    num_candidates: int,
    index_field: str = "fastboard_index",
    path: str = "embedding",
):
    db = get_mongo_client(connection_string).get_database()[collection]

    query_vector = await get_embeddings(query, api_key)

    res = list(
        db.aggregate(
            [
                {
                    "$vectorSearch": {
                        "queryVector": query_vector["body"]["data"][0]["embedding"],
                        "path": path,
                        "limit": limit,
                        "numCandidates": num_candidates,
                        "index": index_field,
                    }
                },
                {"$project": {"embedding": 0}},
            ]
        )
    )

    return parse_response(res)


def parse_response(response):
    if isinstance(response, ObjectId):
        # response = str(response)
        response = "ObjectId('" + str(response) + "')"
    if isinstance(response, Decimal128):
        response = Decimal128.to_decimal(response)

    if isinstance(response, dict):
        for k, v in response.items():
            if isinstance(v, ObjectId):
                # response[k] = str(v)
                response[k] = "ObjectId('" + str(v) + "')"
            if isinstance(v, Decimal128):
                response[k] = Decimal128.to_decimal(v)

    elif isinstance(response, list):
        for item in response:
            if isinstance(item, ObjectId):
                # response[response.index(item)] = str(item)
                response[response.index(item)] = "ObjectId('" + str(item) + "')"
            if isinstance(item, Decimal128):
                response[response.index(item)] = Decimal128.to_decimal(item)
            if isinstance(item, dict):
                for k, v in item.items():
                    if isinstance(v, ObjectId):
                        # item[k] = str(v)
                        item[k] = "ObjectId('" + str(v) + "')"
                    if isinstance(v, Decimal128):
                        item[k] = Decimal128.to_decimal(v)

    return {"body": response}
