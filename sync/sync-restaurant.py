from sync.elastic import ElasticUtils
from sync.mongo import Mongo

mongo = Mongo()
elastic = ElasticUtils('localhost')

query_mongo = {}
mongo_data = mongo.find(query_mongo)

for doc in mongo_data:
    _doc = doc
    _id = doc['_id']
    del _doc['_id']
    if elastic.insertOne(_doc, _id) == 'created':
        print("Inserted doc with _id = {} into index = {}".format(_id, elastic.index))
    else:
        print("Can not insert doc with _id = {} into index = {}".format(_id, elastic.index))
        break
