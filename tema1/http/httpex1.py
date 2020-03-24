import request
import requests
import json

def functie(nume):
    ans = requests.get('https://1.1.1.1/dns-query', params={'name': nume}, headers={'accept': 'application/dns-json'})
    return ans.json()

print(functie('http://fmi.unibuc.ro'))