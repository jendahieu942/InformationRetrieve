import json

from flask import Flask
from flask import render_template

from sync.elastic import QueryBuilders, QueryBuilder, ElasticUtils

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', result="hello")


def hello():
    query = QueryBuilders()
    mainQuery = query.boolQuery() \
        .shouldQuery(QueryBuilder.match_phrase("name", "cơm nhà")) \
        .getQuery()
    elastic = ElasticUtils('localhost', 'information-retrieve')
    result = elastic.search(mainQuery)
    result = json.dumps(result, ensure_ascii=False, indent=4)
    return result


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
