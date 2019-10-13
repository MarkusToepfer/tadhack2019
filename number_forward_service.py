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
import sys
import time
import re
import requests

from http.server import HTTPServer, BaseHTTPRequestHandler
from netaddr import IPNetwork, IPAddress

""" 

    CONFIG is global and living as long as the application is running.

    it will be like:

    {
        "path" : 
        {
            "real_phone_number": "",
            "virtual_number": "",
            "webhook_pathname": "path",
            "api_username": "",
            "api_password": "",
            "account_id": ""
        }

    }

"""

config = {}

def check_config(config):

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
    new     = json.loads(content)

    if (1 == check_config(new)):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')
    else:
        self.send_response(400)

    config[new['webhook_pathname']] = new

    self.end_headers()

    print (f"Configuration dump\n {config}")

""" 

    PROCESS INCOMING COMMAND SMS (orginator == real number)

"""
    
def process_command_sms(handler, message):

    conf      = config[handler.path]
    base_url  = 'https://api.simwood.com/v3/messaging/'
    sms_url   = base_url + conf['account_id'] + "/sms"
    headers   = {   'Content-Type': 'application/json' }

    content   = message['data']['message']

    if (content == "kill"):

        sms = {

            "to"        : conf['real_phone_number'],
            "from"      : conf['virtual_number'],
            "message"   : "We have received your service kill request and shutdown."
        }

        x = requests.post(  sms_url, 
                            data = json.dumps(sms),
                            auth = (conf['api_username'], conf['api_password']))

        print(f"send post request {x} ... {sms}")
        config.pop(handler.path, None)

    if (content.startswith("sms", 0, 3)):

        '''
            Message format for forwarding some number MUST start with 
            sms.

            sms:1234567890:message

        '''

        parts = re.split(":", content)

        if  (parts[0] is None) or (parts[1] is None) or (parts[2] is None):
            print ( "SMS forwarding, failure with message format")
            return

        sms = {

            "to"        : parts[1],
            "from"      : conf['virtual_number'],
            "message"   : parts[2]
        }

        x = requests.post(  sms_url, 
                            data = json.dumps(sms),
                            auth = (conf['api_username'], conf['api_password']))

        print(f"forward sms request {x} ... {sms}")
        return 

    print (f"unknown command received: {message['data']['message']}")

""" 

    PROCESS INCOMING SMS

    example sms

    {
        "app":"sms_inbound",
        "id":"5ed3b4fb955912555cd2569af7c6ea08",
        "data":
        {
            "destination":"447537149184",
            "length":18,
            "message":"Hello World take 2",
            "originator":"4740671620",
            "time":"2019-10-13 08:10:17"
        }
    }

"""
    
def process_sms(handler, incoming_sms_content):

    conf      = config[handler.path]
    base_url  = 'https://api.simwood.com/v3/messaging/'
    sms_url   = base_url + conf['account_id'] + "/sms"
    headers   = {   'Content-Type': 'application/json' }

    message   = json.loads(incoming_sms_content)

    if (message['data']['originator'] == conf['real_phone_number']):
        return process_command_sms(handler, message)

    source    = message['data']['destination']
    content   = message['data']['message']

    print (f" SMS from {source} expected SMS from {conf['virtual_number']} originator {message['data']['originator']}")
    """
        build the forwarding SMS

        we do want to ensurce privacy in both directions, 
        for receiver of the message (over our service), 
        as well as the originatior of the message by cutting the originator number here 

    """

    sms = {

        "to"        : conf['real_phone_number'],
        "from"      : conf['virtual_number'],
        "message"   : content
    }

    x = requests.post(  sms_url, 
                        data = json.dumps(sms),
                        auth = (conf['api_username'], conf['api_password']))

    print(f"send post request {x}")


""" 

    INCOMING SMS

"""

def incoming_sms(self):

    length  = int(self.headers.get('Content-Length'))
    content = self.rfile.read(length)
    
    print (f"Received SMS: {content}")

    # send answer to API (done)

    self.send_response(200)
    self.end_headers()

    process_sms(self, content)

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

        if (self.path == "/configure"):
            return configure(self)

        if (0 == config):
            return error_message(self)

        if self.path in config:
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