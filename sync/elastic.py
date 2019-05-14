import json
import time

from elasticsearch import Elasticsearch


class ElasticUtils:
    def __init__(self, hosts, index=None):
        today = time.strftime('%Y-%m-%d', time.gmtime()).replace('-', '')
        self.es = Elasticsearch([{'host': hosts, 'port': 9200}])
        self.index = index if index is not None else 'information-retrieve-' + today
        self.doc_type = 'restaurants'

    def insertOne(self, _doc, _id):
        res = self.es.index(index=self.index, doc_type=self.doc_type, body=_doc, id=_id)
        return res['result']

    def search(self, query):
        self.es.indices.refresh(index=self.index)
        return self.es.search(index=self.index, body=query)


class QueryBuilders:
    def __init__(self):
        self.query = {}

    def boolQuery(self):
        self.query["query"] = {"bool": {}}
        return self

    def shouldQuery(self, *args):
        should = self.query.get("query").get("bool")
        if len(should) == 0:
            should = [*args]
        else:
            should = self.query['query']['bool']['should']
            should.append(*args)
        self.query['query']['bool']['should'] = should
        return self

    def termQuery(self, term, value):
        self.query['query'] = {'term': {term: value}}
        return self

    def getQuery(self):
        queryStr = json.dumps(self.query)
        return queryStr


class QueryBuilder:
    @staticmethod
    def match(term, value):
        return {"match": {term: value}}

    @staticmethod
    def match_phrase(term, value):
        return {"match_phrase": {term: value}}
