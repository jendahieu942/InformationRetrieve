from crawler.crawler.spiders.restaurant import MongoUtils

print('Test dict')
arr = []
meal = dict()
for i in range(40000, 50000, 1000):
    meal['price'] = i
    meal['name'] = 'Leeteaa'
    meal['desc'] = 'ta quang buu'
    arr.append(meal)

print(len(arr))
for el in arr:
    print(el)

print('Test sha hashing')
salt = 'test sha hashing'
import hashlib

key = hashlib.sha256(salt.encode()).hexdigest()
print(key)

print("\nTest find key mongo")
mongo = MongoUtils('hieutv', 'info_retrieve')
items = mongo.findByID(key)
print(items.count())
