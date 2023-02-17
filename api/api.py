from concurrent.futures.thread import _threads_queues
import json
from flask import Flask, request, jsonify
from pglast import parser as p
import queryParser as qp
import phraseGenerator as pg

app = Flask(__name__)

invalidSQLMessage = "Invalid."

@app.after_request
def add_cors_header(response):
    response.headers['Access-Control-Allow-Origin'] = "https://query-pe.dev"
    response.headers['Access-Control-Allow-Headers'] = "Content-Type,Authorization"
    response.headers['Access-Control-Allow-Methods'] = "GET,PUT,POST,DELETE,OPTIONS"
    return response

@app.route('/parse', methods=['GET', 'POST'])
def parseTree():
    try:
        data = json.loads(request.data)
        parseTree = p.parse_sql_json(data['inputQuery'])
        dictionaryTree = qp.extractClauseData(parseTree)
        resObj = {}
        resObj['dict'] = dict(dictionaryTree)
        tempVar = 5

        # Path for JSON Tree
        if data['path'] == 1:
            jsonParseTree = json.loads(parseTree)
            formattedStatement = jsonParseTree['stmts'][0]['stmt']
            resObj['output'] = json.dumps(formattedStatement)
            return jsonify(resObj)

        # Path for Parsed Results
        if data['path'] == 2:
            phrases = pg.extractPhrases(dictionaryTree)
            resObj['output'] = phrases
            return jsonify(resObj)
    except Exception:
        return jsonify(invalidSQLMessage)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)