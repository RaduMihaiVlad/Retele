from flask import Flask, jsonify
from flask import request

app = Flask(__name__)

@app.route('/')
def hello():
    return "Apare in browser ceva interesant"

'''
This method expects a json content.
Use header: 'Content-Type: application/json'
'''
@app.route('/post', methods=['POST'])
def post_method():
    print ("Got from user: ", request.get_json())
    return jsonify({'got_it': request.get_json()['value'] *
    						  request.get_json()['value']})


@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)