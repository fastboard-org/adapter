import pymongo
from bson.objectid import ObjectId


async def execute_query(
    connection_string: str,
    collection: str,
    method: str,
    filter_body: dict,
    update_body: dict,
):
    client = pymongo.MongoClient(connection_string)
    db = client.get_database()[collection]
    switcher = {
        "aggregate": db.aggregate,
        "count": db.count_documents,
        "distinct": db.distinct,
        "find": db.find,
        "findOne": db.find_one,
        "findOneAndDelete": db.find_one_and_delete,
        "findOneAndReplace": db.find_one_and_replace,
        "findOneAndUpdate": db.find_one_and_update,
        "insertOne": db.insert_one,
        "insertMany": db.insert_many,
        "updateOne": db.update_one,
        "updateMany": db.update_many,
        "deleteOne": db.delete_one,
        "deleteMany": db.delete_many,
    }
    print(
        f"{method} on {collection}\n Filter: {filter_body}\n Update: {update_body}"
    )
    res = switcher.get(method)(filter_body, update_body)
    if res:
        for k, v in res.items():
            if isinstance(v, ObjectId):
                res[k] = str(v)
    return res
