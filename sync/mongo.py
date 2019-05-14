from pymongo import MongoClient


class Mongo:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017')
        self.database = self.client['hieutv']
        self.collection = self.database['info_retrieve']

    def find(self, query=None):
        if query is None or query == {}:
            print('Query default')
            data = self.collection.find()
        else:
            print('Query with specify query')
            data = self.collection.find(query)
        return data

