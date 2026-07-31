# PI_DEPLOY — Deploy Portfolio-Django on Orange Pi / Raspberry Pi

## 1. Prerequisites

- Orange Pi or Raspberry Pi with fresh OS (Armbian / Raspberry Pi OS Lite)
- Domain name pointing to Cloudflare (DNS proxied — orange cloud)
- SSH access configured with key-based auth
- Deploy user `<user>` (e.g. `opi`) who owns the project. **Gunicorn runs as this user, not `www-data`.**
- Python note: the Pi (Debian Trixie / Armbian) ships Python 3.13 by default. The project needs `Django>=5.1` to work on 3.13 (the repo pins 5.2.1, which is fine). If you ever see `ModuleNotFoundError: No module named 'cgi'`, the installed Django is too old for Python 3.13.

## 2. System Dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv nodejs npm git nginx ufw
```

## 3. Clone & Setup

```bash
cd ~
git clone https://github.com/yohi441/portfolio-django.git
cd portfolio-django

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn
pip install --upgrade gunicorn

npm install
npm run build:css

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

> **Note:** `pip install --upgrade gunicorn` is required on Python 3.13 to avoid the `pkg_resources` error. If you ever recreate the venv (e.g. after a Python upgrade), delete it and repeat the steps above.

## 4. Environment Variables

Create `/home/<user>/portfolio-django/.env` (as the deploy user, not root):

```
SECRET_KEY=<your-django-secret-key>
DEBUG=False
ALLOWED_HOSTS=localhost,yourdomain.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your@email.com
EMAIL_HOST_PASSWORD=<app-password>
```

## 5. Gunicorn (systemd Service)

Create `/etc/systemd/system/portfolio.service`:

```ini
[Unit]
Description=Portfolio Django — Gunicorn
After=network.target

[Service]
User=<user>
Group=<user>
WorkingDirectory=/home/<user>/portfolio-django
Environment=HOME=/home/<user>/portfolio-django
EnvironmentFile=/home/<user>/portfolio-django/.env
ExecStart=/home/<user>/portfolio-django/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    --access-logfile /var/log/portfolio/access.log \
    --error-logfile /var/log/portfolio/error.log \
    mysite.wsgi:application

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

> **Note:** `Environment=HOME=/home/<user>/portfolio-django` is important. Without it, `python-decouple` looks for `.env` in the user's home directory and crashes with `Permission denied: '/root'` when run via systemd.

```bash
sudo mkdir -p /var/log/portfolio
sudo chown -R <user>:<user> /var/log/portfolio
sudo systemctl daemon-reload
sudo systemctl enable --now portfolio
sudo systemctl status portfolio
```

## 6. Nginx (Reverse Proxy)

Create `/etc/nginx/sites-available/portfolio`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    client_max_body_size 10M;

    location /static/ {
        alias /home/<user>/portfolio-django/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/portfolio /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl enable --now nginx
```

## 7. Cloudflare Tunnel

Install `cloudflared`:

```bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared
```

Authenticate & create tunnel:

```bash
cloudflared tunnel login
cloudflared tunnel create portfolio
cloudflared tunnel route dns portfolio yourdomain.com
```

Create `~/.cloudflared/config.yml`:

```yaml
tunnel: <tunnel-id>
credentials-file: /home/<user>/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: yourdomain.com
    service: http://localhost:80
  - service: http_status:404
```

Install as systemd service:

```bash
sudo cloudflared service install
sudo systemctl enable --now cloudflared
```

**Security note:** Once the tunnel is working, disable direct port 80 access by removing nginx listen or binding to localhost only. The tunnel routes through Cloudflare's edge — no public ports needed.

## 8. Security

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw enable

sudo apt install -y fail2ban unattended-upgrades
sudo systemctl enable --now fail2ban
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

## 9. Backup (Daily Cron)

```bash
sudo crontab -e
```

```
0 3 * * * cp /home/<user>/portfolio-django/db.sqlite3 /backups/portfolio/db-$(date +\%Y\%m\%d).sqlite3 && find /backups/portfolio -name '*.sqlite3' -mtime +30 -delete
```

## 10. Maintenance

```bash
# Update project
cd /home/<user>/portfolio-django
git pull
source venv/bin/activate
pip install -r requirements.txt
npm run build:css
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart portfolio

# View logs
sudo journalctl -u portfolio -f
sudo tail -f /var/log/portfolio/access.log

# Check tunnel
cloudflared tunnel list
cloudflared tunnel info portfolio
```

## 11. Troubleshooting

| Problem | Check |
|---------|-------|
| 502 Bad Gateway | `sudo systemctl status portfolio`, `journalctl -u portfolio -n 20` |
| Static files 404 | `ls /home/<user>/portfolio-django/staticfiles/`, nginx static alias path |
| Domain not loading | `cloudflared tunnel list`, `cloudflared tunnel route list` |
| Email not sending | Check `.env` credentials, port 587 outbound |
| `ModuleNotFoundError: No module named 'cgi'` | Installed Django too old for Python 3.13 — `pip install --upgrade django` (needs >= 5.1) |
| `Permission denied: '/root'` | `python-decouple` can't find `.env` — make sure `Environment=HOME=/home/<user>/portfolio-django` is set in the service and the `.env` file exists |
| `No module named 'pkg_resources'` | Recreate venv or `pip install --upgrade gunicorn` |
| Permission denied writing files | Project must be owned by the deploy user: `sudo chown -R <user>:<user> /home/<user>/portfolio-django` |
