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

import argparse
import json
import ssl
import requests

from http.server import HTTPServer, BaseHTTPRequestHandler
from netaddr import IPNetwork, IPAddress

""" 

    CONFIG is global and living as long as the application is running.

    {
      "real_phone_number": "",
      "virtual_number": "",
      "webhook_pathname": "",
      "api_username": "",
      "api_password": "",
      "account_id": ""
    }

"""

config = {}

def check_config():

    print(f"Checking config: {config}")

    if 'real_phone_number' in config:
        print ("Config key 'real_phone_number' with content:" + config["real_phone_number"])
    else:
        print ("Config without key 'real_phone_number'")
        return 0

    if 'virtual_number' in config:
        print ("Config key 'virtual_number' with content:" + config['virtual_number'])
    else:
        print ("Config without key 'virtual_number'")
        return 0

    if 'webhook_pathname' in config:
        print ("Config key 'webhook_pathname' with content:" + config['webhook_pathname'])
    else:
        print ("Config without key 'webhook_pathname'")
        return 0

    if 'api_username' in config:
        print ("Config key 'api_username' with content:" + config['api_username'])
    else:
        print ("Config without key 'api_username'")
        return 0

    if 'api_password' in config:
        print ("Config key 'api_password' with content:" + config['api_password'])
    else:
        print ("Config without key 'api_password'")
        return 0

    if 'account_id' in config:
        print ("Config key 'account_id' with content:" + config['account_id'])
    else:
        print ("Config without key 'account_id'")
        return 0

    return 1

""" 

    REQUESTS will be accepted by the simwood IPs only.

"""

def request_from_simwood_ip(address):

    print(f"Checking address {address}")

    if IPAddress(address) in IPNetwork("178.22.139.84/31"):
        return 1

    if IPAddress(address) in IPNetwork("185.63.140.84/31"):
        return 1

    if IPAddress(address) in IPNetwork("185.63.141.84/31"):
        return 1

    if IPAddress(address) in IPNetwork("185.63.142.84/31"):
        return 1

    if IPAddress(address) in IPNetwork("185.63.143.84/31"):
        return 1

    return 0

""" 

    CONFIGURATION

"""

def configure(self):

    global config

    print ("Received configuration request")

    length  = int(self.headers.get('Content-Length'))
    content = self.rfile.read(length)
    config  = json.loads(content)

    if (1 == check_config()):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')
    else:
        self.send_response(400)


    self.end_headers()

""" 

    SEND SMS

"""

def sending_sms(self):

    print ("Sending SMS")

    base_url  = 'https://api.simwood.com/v3/messaging/'
    sms_url   = base_url + config['account_id'] + "/sms"
    headers   = {   'Content-Type': 'application/json' }

    message   = {  
            
    }

    content = json.dumps(message)

    x = requests.post(  sms_url, 
                        data = content,
                        auth = HTTPDigestAuth(
                            config['api_username'], 
                            config['api_username']))

""" 

    PROCESS INCOMING SMS

"""

def process_sms(self, message):

    print ("Processing SMS")

    length  = int(self.headers.get('Content-Length'))
    content = self.rfile.read(length)
    #message = json.loads(content)
    
    print (f"SMS content {content}")

    self.send_response(200)
    self.end_headers()

""" 

    INCOMING SMS

"""

def incoming_sms(self):

    print ("Received SMS")

    length  = int(self.headers.get('Content-Length'))
    content = self.rfile.read(length)
    #message = json.loads(content)
    
    print (f"SMS content {content}")

    self.send_response(200)
    self.end_headers()

    #process_sms(self, message)

""" 

    ERROR 

"""

def error_message(self):
    self.send_response(400)
    self.end_headers()

""" 

    HTTP RUNTIME SETUP

"""

class request_handler(BaseHTTPRequestHandler):

    def do_GET(self):

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        content = "<html><body><h1>This is a very basic number forward service.</h1></body></html>"
        self.wfile.write(content.encode("utf8"))

    def do_POST(self):

        print (f"Receiving POST at path: {self.path}")

        if (self.path == "/sms"):
            return incoming_sms(self)

        if (self.path == "/configure"):
            return configure(self)

        if (0 == config):
            return error_message(self)

        if config.get('webhook_pathname') is None:
            return error_message(self)

        if (self.path == config['webhook_pathname']):
            return incoming_sms(self)

        return error_message(self)

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

        return 

def run(server_class=HTTPServer, handler_class=request_handler, addr="localhost", port=8000):
    
    server_address = (addr, port)
    httpd = server_class(server_address, handler_class)

    print(f"Starting httpd server on {addr}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run a simple HTTP server")
    parser.add_argument(
        "-l",
        "--listen",
        default="localhost",
        help="Specify the IP address on which the server listens",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="Specify the port on which the server listens",
    )
    args = parser.parse_args()
    run(addr=args.listen, port=args.port)