from concurrent.futures.thread import _threads_queues
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from pglast import parser as p
import queryParser as qp
import phraseGenerator as pg

app = Flask(__name__)
CORS(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

invalidSQLMessage = "Invalid."

@app.route('/parse', methods=['GET', 'POST'])
def parseTree():
    tempVar = 0
    try:
        tempVar = 1
        data = json.loads(request.data)
        tempVar = 2
        parseTree = p.parse_sql_json(data['inputQuery'])
        tempVar = 3
        dictionaryTree = qp.extractClauseData(parseTree)
        tempVar = 4
        resObj = {}
        resObj['dict'] = dict(dictionaryTree)
        tempVar = 5

        # Path for JSON Tree
        if data['path'] == 1:
            jsonParseTree = json.loads(parseTree)
            tempVar = 6
            formattedStatement = jsonParseTree['stmts'][0]['stmt']
            resObj['output'] = json.dumps(formattedStatement)
            return jsonify(resObj)

        # Path for Parsed Results
        if data['path'] == 2:
            phrases = pg.extractPhrases(dictionaryTree)
            tempVar = 6
            resObj['output'] = phrases
            return jsonify(resObj)
    except Exception as e:
        exceptionRes = {}
        exceptionRes['state'] = tempVar
        exceptionRes['message'] = str(e)
        return jsonify(str(exceptionRes))