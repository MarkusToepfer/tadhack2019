# tadhack2019
Tadhack 2019 

## Prerequisties

SSL enabled server
The python server should be startet behind some proxy. 

### Example nginx proxy config

This example config was used for testing to host the SSL proxy at 
https://markustoepfer.com:8080 and run the python server at http://localhost:8000 on the same maschine.

~~~
server {

    listen 8080 ssl;

    ssl on;
    ssl_certificate /etc/ssl/private/markustoepfer.com_bundle.crt;
    ssl_certificate_key /etc/ssl/private/markustoepfer.com.key;

    location / {
        proxy_pass http://localhost:8000;
    }

}
~~~
