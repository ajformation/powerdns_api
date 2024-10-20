
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

## Certificat

Récupérer un certificat avec certbot

```shell
sudo apt install certbot
sudo certbot certonly --standalone -d app.domain.net
```

## Liens

- <https://zhangtemplar.github.io/flask/>
- <https://blog.miguelgrinberg.com/post/running-a-flask-application-as-a-service-with-systemd>
- <https://blog.container-solutions.com/running-docker-containers-with-systemd>
- <https://certbot.eff.org/instructions?ws=apache&os=pip>
- <https://stackoverflow.com/questions/49306970/correct-input-type-for-ip-address>
- <https://gist.github.com/jonstout/f3eb6cf002ebe610a48ade6b9f948762>
