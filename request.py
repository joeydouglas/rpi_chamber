import requests
url = 'http://192.168.1.220:8086/write?db=meatsack'
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
payload = "tested02,host=server01,region=us-west value=0.64 1434055562000000000\n"
r = requests.post(url, data=payload, headers=headers)
r.raw
