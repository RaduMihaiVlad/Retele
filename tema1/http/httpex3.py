import json

import requests

url = 'http://rt1:8001/post'
headers = {'Content-Type': 'application/json'}
data = {'value': 5}
print(requests.post(url, data=json.dumps(data), headers=headers).content)

