import flask
from flask import request, jsonify

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return "Chauconnect API for Casino"

def test():
    test_data = [ {"test1": "hi", "test2": 1312} ]
    return jsonify(test_data)

app.run()
