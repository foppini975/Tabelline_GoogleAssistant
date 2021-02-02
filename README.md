# Tabelline_GoogleAssistant


## Localenv setup
```bash
python3 -m venv localenv
source ./localenv/bin/activate
pip install -r requirements.txt
```

## /etc/systemd/system/tabelline.service
```
; this file has to be placed in /etc/systemd/system/tabelline.service
[Unit]
Description=Gunicorn instance to serve Tabelline API
After=network.target

[Service]
User=fabio
Group=www-data
WorkingDirectory=/home/fabio/myProjects/Tabelline_DF
Environment="PATH=/home/fabio/myProjects/Tabelline_DF/localenv/bin"
ExecStart=/home/fabio/myProjects/Tabelline_DF/localenv/bin/gunicorn --workers 3 --bind unix:tabelline.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```

## Restart and show logs:
```bash
sudo systemctl restart tabelline.service; sudo journalctl -f -u tabelline
```

## Nginx configuration
```
    location /tabelline {
      proxy_set_header        Host $host;
      proxy_set_header        X-Real-IP $remote_addr;
      proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header        X-Forwarded-Proto $scheme;

      proxy_pass          http://unix:/home/fabio/myProjects/Tabelline_DF/tabelline.sock;
      proxy_read_timeout  90;

    }
```
