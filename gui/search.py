import json

from flask import Flask, request
from flask import render_template

from sync.elastic import QueryBuilders, QueryBuilder, ElasticUtils

app = Flask(__name__)
elastic = ElasticUtils('localhost', 'information-retrieve')


def queryGenerate(user_query):
    query = QueryBuilders()
    mainQuery = query.boolQuery() \
        .shouldQuery(QueryBuilder.match_phrase("name", )) \
        .getQuery()


@app.route('/')
def index():
    return render_template('index.html', result="hello")


@app.route('/search', methods=['GET'])
def search():
    data = request.args.get('query')
    return render_template('result.html', result=data)


if __name__ == '__main__':
    app.run(host='localhost', debug=False, port=50001)
