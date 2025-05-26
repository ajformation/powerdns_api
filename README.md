# powerdns_api

## Lancé avec Gunicorn

```systemd
[Unit]
Description=DNS Change microserver
After=network.target

[Service]
User=jerome
WorkingDirectory=/home/user/powerdns_api
ExecStart=/home/user/powerdns_api/.venv/bin/gunicorn \
                --certfile cert.pem \
                --keyfile key.pem \
                --bind [::]:5000 \
                --reload  \
                webapp:app
Restart=always

[Install]
WantedBy=multi-user.target
```

## Docker

```shell
$ docker run \
        --env ZONE=example.net \
        --env PORT=6667 \
        -v ./config/:/app/config/ \
        -p 6667:6667 \
        djayroma/powerdns_api:latest
```

With Certificates :

```shell
$ docker run \
        --env ZONE=example.net \
        --env PORT=6667 \
        -v ./config/:/app/config/ \
        -v ./mycert.pem:/app/cert.pem \
        -v ./mykey.pem:/app/key.pem \
        -p 6667 \
        djayroma/powerdns_api:latest
```

## Certificat

### Récupérer un certificat avec certbot

```shell
sudo apt install certbot
sudo certbot certonly --standalone -d app.domain.net
```

### Générer un certificat snakeoil

```shell
openssl req  -nodes -new -x509  \
    -keyout key.pem \
    -out cert.pem \
    -subj "/C=FR/ST=FR/L=City/O=company/OU=Com/CN=localhost"
```

## Liens

- <https://zhangtemplar.github.io/flask/>
- <https://blog.miguelgrinberg.com/post/running-a-flask-application-as-a-service-with-systemd>
- <https://blog.container-solutions.com/running-docker-containers-with-systemd>
- <https://certbot.eff.org/instructions?ws=apache&os=pip>
- <https://stackoverflow.com/questions/49306970/correct-input-type-for-ip-address>
- <https://gist.github.com/jonstout/f3eb6cf002ebe610a48ade6b9f948762>
