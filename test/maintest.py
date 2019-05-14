# from crawler.crawler.spiders.restaurant import MongoUtils
#
# print('Test dict')
# arr = []
# meal = dict()
# for i in range(40000, 50000, 1000):
#     meal['price'] = i
#     meal['name'] = 'Leeteaa'
#     meal['desc'] = 'ta quang buu'
#     arr.append(meal)
#
# print(len(arr))
# for el in arr:
#     print(el)
#
# print('Test sha hashing')
# salt = 'test sha hashing'
# import hashlib
#
# key = hashlib.sha256(salt.encode()).hexdigest()
# print(key)
#
# print("\nTest find key mongo")
# mongo = MongoUtils('hieutv', 'info_retrieve')
# items = mongo.findByID(key)
# print(items.count())
import time
from datetime import datetime

from sync.elastic import ElasticUtils, QueryBuilders, QueryBuilder

query = QueryBuilders()
mainQuery = query.boolQuery() \
    .shouldQuery(QueryBuilder.match_phrase("name", "cơm nhà")) \
    .getQuery()
elastic = ElasticUtils('localhost', 'information-retrieve')
result = elastic.search(mainQuery)
print(result)

print(time.strftime('%Y-%m-%d', time.gmtime()).replace('-', ''))
# print(str(datetime.now()).split(' ')[0].replace('-', ''))
#
