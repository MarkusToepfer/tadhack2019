#usr/bin/env python

"""
Copyright 2019 Markus Töpfer

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

__author__  = "Markus Töpfer"
__license__ = "Apache Version 2"
__version__ = "1.0"

The HTTP server part (HTTP RUNTIME SETUP) is based on the example of Brad Montgomery 
https://gist.github.com/bradmontgomery/2219997
"""

import requests
import json

'''
{
  "real_phone_number": "",
  "virtual_number": "",
  "webhook_pathname": "",
  "api_username": "",
  "api_password": "",
  "account_id": ""
}
'''

local  = 'http://localhost:8000'
url    = 'https://markustoepfer.com:8080/configure'
config = {	
			'real_phone_number': '491234567890',
			'virtual_number': 	 '441234567890',
			'webhook_pathname':  '/test/dummy',
			'api_username': 	 'name',
  			'api_password': 	 'password',
  			'account_id': 	 	 'id'
		}

content = json.dumps(config)

x = requests.post(url, data = content)

print(x.headers.items)
print(x.text)