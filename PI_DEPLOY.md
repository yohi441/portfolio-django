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
ALLOWED_HOSTS=localhost,portfolio.yourdomain.com
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
    server_name portfolio.yourdomain.com;

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

> **Orange Pi One note:** the Orange Pi One runs the Allwinner H3 (Cortex-A7, 32-bit ARMv7). Install the **32-bit** `cloudflared-linux-arm` binary — the `arm64` build fails with `Exec format error`.

### 7.1 Full DNS setup (required for tunnel routing)

The tunnel's Public Hostname route must be configured in the Cloudflare dashboard, which requires the domain to be an **active zone** in your Cloudflare account:

1. dash.cloudflare.com → **Add a site** → **Connect a domain** → enter your domain → **Free** plan.
2. Cloudflare scans your DNS records. No changes needed — but if you have email on the domain, keep any MX/SPF/DMARC/DKIM records.
3. Copy the **2 nameservers** Cloudflare shows you.
4. At your registrar (e.g. Hostinger hPanel → Domains → your domain → **Nameservers**), replace the registrar's nameservers with Cloudflare's 2 nameservers.
5. Wait for the zone to show **Active** in Cloudflare (usually ~15 min, up to 24 h).

### 7.2 Install the connector (token method)

```bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared
cloudflared --version
```

> With the token method there is **no** `cloudflared tunnel login` / `tunnel create` / `config.yml`. The connector fetches its config from Cloudflare, so the token is the only credential you need.

### 7.3 Create the tunnel & get the token

1. Zero Trust (one.dash.cloudflare.com) → **Networks → Tunnels** → **Create a tunnel** → give it a name.
2. Copy the **token** (starts with `eyJ...`) — it is shown only once and embeds the tunnel ID + credentials.
3. On the Pi:

```bash
sudo cloudflared service install <TOKEN>
sudo systemctl enable --now cloudflared
```

The tunnel shows **Healthy** once the connector connects. To find the tunnel ID later: Zero Trust → Networks → Tunnels → tunnel → **Overview**, or `cat /etc/cloudflared/config.yml` on the Pi.

### 7.4 Route your subdomain

Once the zone is **Active**:

1. Zero Trust → **Networks → Tunnels** → your tunnel → **Public Hostname** → **Add a public hostname**.
2. Subdomain: `portfolio` · Domain: your domain · Type: **HTTP** · URL: **`http://localhost:80`**.
3. Cloudflare auto-creates the DNS CNAME and a free SSL certificate.

> **502 Bad Gateway?** The Public Hostname Service URL must be `http://localhost:80` (HTTP, port 80). If it's `https://localhost`, port 443, or the domain itself, requests fail with 502 even when the origin works.

### 7.5 Point the app at the subdomain

- Nginx: `server_name portfolio.yourdomain.com;` → `sudo nginx -t && sudo systemctl reload nginx`
- `.env`: `ALLOWED_HOSTS=localhost,portfolio.yourdomain.com` → `sudo systemctl restart portfolio`

**Security note:** with the tunnel active, public traffic only reaches the Pi through Cloudflare's edge. UFW's default *deny incoming* (Section 8) blocks direct port 80 access — exactly what you want. No public ports needed.

### 7.6 Tailscale (optional — remote SSH from anywhere)

Tailscale builds a private WireGuard mesh between your devices (free personal plan: 100 devices / 3 users, ~15–40 MiB RAM). Use it to SSH from outside the LAN without exposing port 22.

```bash
# On the Pi
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
# Open the printed URL and sign in with your account

# Allow the tailnet through UFW (default is deny incoming)
sudo ufw allow in on tailscale0 to any port 22 proto tcp
```

On your client device, install Tailscale and sign in with the **same account**. Then SSH from anywhere:

```bash
ssh opi@<pi-tailnet-ip>    # e.g. 100.x.x.x — run `tailscale ip` on the Pi
# or with MagicDNS: ssh opi@orangepione
```

`tailscale up --ssh` / `tailscale set --ssh=true` enables Tailscale's built-in SSH auth instead of managing keys; plain `tailscale up` just makes the Pi reachable over the tailnet using your existing SSH keys.

> For GitHub Actions CI/CD over the tailnet, Tailscale SSH lets the runner log in with **no keys** — it authenticates by its `tag:ci` tailnet identity. Keep `tailscale set --ssh=true` on and grant `tag:ci` access in the ACL (Section 11).

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

## 11. CI/CD (GitHub Actions)

On every push to `main`, GitHub Actions runs Django checks + tests, then SSHes into the Pi and runs `deploy.sh`.

### One-time Pi setup

1. Ensure the repo is already cloned at `/home/<user>/portfolio-django` (Section 3).
2. The deploy user needs passwordless `systemctl restart` for the service:

   ```bash
   sudo visudo -f /etc/sudoers.d/portfolio
   ```

   ```
   <user> ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart portfolio
   ```

3. `git pull` must work without a password prompt. If the repo is private, set up an SSH key or a [fine-grained PAT](https://github.com/settings/personal-access-tokens) for the deploy user. For a public repo, HTTPS works out of the box.
4. The workflow file is `.github/workflows/deploy.yml`; the deploy script is `deploy.sh` at the repo root (pulled by git before each run).
5. Tailscale SSH must be enabled on the Pi: `sudo tailscale set --ssh=true`. The runner authenticates by Tailscale identity — no SSH keys needed (see secrets below).

### GitHub repository secrets

Create these under **Settings → Secrets and variables → Actions**:

| Secret | Value |
|--------|-------|
| `TS_OAUTH_CLIENT_ID` | OAuth client ID from login.tailscale.com/admin/settings/oauth |
| `TS_OAUTH_SECRET` | OAuth client secret for the same client |
| `PI_HOST` | The Pi's **tailnet IP** (e.g. `100.x.x.x` — run `tailscale ip` on the Pi) |
| `PI_USER` | Deploy user (e.g. `opi`) |

> This setup uses **Tailscale SSH — no SSH keys at all**. The runner joins the tailnet as an ephemeral `tag:ci` node and authenticates by Tailscale identity. Create the OAuth client at login.tailscale.com/admin/settings/oauth (scopes: Devices Core Write + Keys Auth Keys Write, tag: `tag:ci`), then add the rules below to the ACL (one.dash.cloudflare.com → Access controls → ACL) so `tag:ci` can SSH to the Pi. The Pi must be tagged `tag:pi` (see below) — **SSH rule destinations must be tags, not IPs or hostnames** (`Error: invalid dst` otherwise):

```json
"grants": [
  { "src": ["*"], "dst": ["*"], "ip": ["*"] }
],
"tagOwners": {
  "tag:ci": ["autogroup:admin"],
  "tag:pi": ["autogroup:admin"]
},
"ssh": [
  { "action": "accept", "src": ["tag:ci"], "dst": ["tag:pi"], "users": ["root", "autogroup:nonroot"] }
]
```

> Apply the tag on the Pi: `sudo tailscale up --advertise-tags=tag:pi --ssh` (mention `--ssh` too — it's non-default), approve the Re-authentication URL, and confirm with `tailscale status` that the Pi shows `tag:pi`. See the troubleshooting section for the full sequence.

> If you prefer classic SSH keys instead, keep a `PI_SSH_KEY` secret (ed25519, no passphrase) whose public half is in the deploy user's `~/.ssh/authorized_keys`.

### Manual deploy

```bash
gh workflow run deploy.yml
```

## 12. Troubleshooting

### Tailscale SSH: runner can't connect ("tailnet policy does not permit you to SSH to this node")

Tailscale rejects IPs and hostnames as `dst` in SSH rules (`Error: invalid dst`) — SSH destinations must be **tags**. The runner authenticates by its `tag:ci` identity. Fix in this order:

1. Define the Pi's tag in the ACL — `tag:pi` must exist in `tagOwners` *before* it's referenced, or you get `Error: tag not found: "tag:pi"`:

   ```json
   "tagOwners": {
       "tag:ci": ["autogroup:admin"],
       "tag:pi": ["autogroup:admin"]
   }
   ```

2. Add the SSH rule (src `tag:ci` → dst `tag:pi`), save, and verify with the Preview button:

   ```json
   "ssh": [
       { "action": "accept", "src": ["tag:ci"], "dst": ["tag:pi"], "users": ["autogroup:nonroot", "root"] }
   ]
   ```

3. Apply the tag on the Pi — **must use `tailscale up`, not `tailscale set`** (`set` has no tag flag: `flag provided but not defined: -advertise-tags`), and mention all non-default flags or it refuses:

   ```bash
   sudo tailscale up --advertise-tags=tag:pi --ssh
   # if you forget --ssh: "changing settings via 'tailscale up' requires
   # mentioning all non-default flags" → re-run with --ssh added
   ```

   Approve any Re-authentication URL it prints (instant as admin).

4. Verify the tag landed, then re-run the deploy:

   ```bash
   tailscale status   # Pi line must end with tag:pi
   gh workflow run deploy.yml
   ```

| Problem | Check |
|---------|-------|
| 502 Bad Gateway (origin) | `sudo systemctl status portfolio`, `journalctl -u portfolio -n 20` |
| Tunnel 502 / Host error | Public Hostname Service URL must be `http://localhost:80`; verify origin with `curl -I http://localhost/` on the Pi |
| Domain not loading | Zero Trust → Networks → Tunnels → tunnel status **Healthy**; check the zone is **Active** and the Public Hostname is configured |
| `Exec format error` on cloudflared | 32-bit Pi installed the `arm64` binary — install `cloudflared-linux-arm` |
| `cloudflared tunnel list` cert.pem error | Expected with token tunnels (no cert.pem) — get the tunnel ID from the dashboard or `cat /etc/cloudflared/config.yml` |
| Email not sending | Check `.env` credentials, port 587 outbound |
| `ModuleNotFoundError: No module named 'cgi'` | Installed Django too old for Python 3.13 — `pip install --upgrade django` (needs >= 5.1) |
| `Permission denied: '/root'` | `python-decouple` can't find `.env` — make sure `Environment=HOME=/home/<user>/portfolio-django` is set in the service and the `.env` file exists |
| `No module named 'pkg_resources'` | Recreate venv or `pip install --upgrade gunicorn` |
| `tailnet policy does not permit you to SSH to this node` | Tailscale SSH reached the Pi but the ACL denies `tag:ci` — the SSH `dst` must be `tag:pi` (not an IP/hostname); add the accept rule and ensure `tagOwners` defines `tag:pi` (see above) |
| `Permission denied (publickey,password)` over the tailnet | Tailscale SSH is off on the Pi — `sudo tailscale set --ssh=true` |
| Permission denied writing files | Project must be owned by the deploy user: `sudo chown -R <user>:<user> /home/<user>/portfolio-django` |
