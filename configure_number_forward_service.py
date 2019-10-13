import requests
import json

'''
{
  "real_phone_number": 447123123123"",
  "virtual_number": "447537149184",
  "webhook_pathname": "/sample-webhook/calls"
}
'''

local  = 'http://localhost:8000'
url    = 'https://markustoepfer.com:8080/configure'
config = {	
			'real_phone_number': '4915167722528',
			'virtual_number': '447537149204',
			'webhook_pathname': '/test/dummy',
		}

content = json.dumps(config)

x = requests.post(url, data = content)

print(x.headers.items)
print(x.text)