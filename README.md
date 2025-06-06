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

### Dehydrated

```shell
url=https://github.com/dehydrated-io/dehydrated/archive/master.tar.gz
mkdir /srv/dehydrated
chown www-data:www-data /srv/dehydrated
wget -P /srv $url
cd /srv
tar xf $(basename $url)
cat > /etc/nginx/sites-enabled/default <<EOF

        location ^~ /.well-known/acme-challenge {
                alias /srv/dehydrated;
        }
EOF
vim /etc/nginx/sites-enabled/default
systemctl restart nginx
cd /srv/dehydrated-master
./dehydrated --register --accept-terms

```

### ACME.sh

```shell
su - homer
MAIL=homer@example.org
curl https://get.acme.sh | sh -s email=${MAIL}
acme.sh --install-cert --domain donut.example.net --reloadcmd 'sudo systemctl restart powerdnsapi' --key-file <path>/key.pem --fullchain-file <path>/cert.pem --webroot /srv/acme

```

## Liens

- <https://zhangtemplar.github.io/flask/>
- <https://blog.miguelgrinberg.com/post/running-a-flask-application-as-a-service-with-systemd>
- <https://blog.container-solutions.com/running-docker-containers-with-systemd>
- <https://certbot.eff.org/instructions?ws=apache&os=pip>
- <https://stackoverflow.com/questions/49306970/correct-input-type-for-ip-address>
- <https://gist.github.com/jonstout/f3eb6cf002ebe610a48ade6b9f948762>
