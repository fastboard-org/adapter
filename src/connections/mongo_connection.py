import pymongo
from bson.code import Code
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
        "deleteOne": db.delete_one,
        "deleteMany": db.delete_many,
        "distinct": db.distinct,
        "find": db.find,
        # "findAndModify": db.__find_and_modify,
        "findOne": db.find_one,
        "findOneAndDelete": db.find_one_and_delete,
        "findOneAndReplace": db.find_one_and_replace,
        "findOneAndUpdate": db.find_one_and_update,
        "insertOne": db.insert_one,
        "insertMany": db.insert_many,
        "updateOne": db.update_one,
        "updateMany": db.update_many,
    }
    res = switcher.get(method)(filter_body, update_body)
    print(res, type(res))
    # change all objectIDs on res to strings
    for k, v in res.items():
        if isinstance(v, ObjectId):
            res[k] = str(v)
    return res


"""
export enum MONGO_METHOD {
  AGGREGATE = "aggregate",
  COUNT = "count",
  DELETE_ONE = "deleteOne",
  DELETE_MANY = "deleteMany",
  DISTINCT = "distinct",
  FIND = "find",
  FIND_AND_MODIFY = "findAndModify",
  FIND_ONE = "findOne",
  FIND_ONE_AND_DELETE = "findOneAndDelete",
  FIND_ONE_AND_REPLACE = "findOneAndReplace",
  FIND_ONE_AND_UPDATE = "findOneAndUpdate",
  INSERT_ONE = "insertOne",
  INSERT_MANY = "insertMany",
  UPDATE_ONE = "updateOne",
  UPDATE_MANY = "updateMany",
}
"""
