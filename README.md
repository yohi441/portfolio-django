# portfolio-django

This is my personal portfolio built with Django.

## Tech Stack

- Python 3.12 / 3.13
- Django 5.2
- Tailwind CSS
- htmx
- Alpine.js
- Whitenoise (static files)
- Gunicorn (production)
- Nginx (reverse proxy)
- Deployed on Orange Pi One

## Features

- Portfolio of 9 projects (MyBooksite, Django Job Board API, FastAPI Recipe API, Go URL Shortener, Chatapp, Clinic Manager, Portfolio Site, Chick Thermo System, CovidTracker)
- HTMX lazy-loading project sections (Load More)
- Learning section (Go, Homelabing, IoT, DevOps)
- Contact form with email notifications

## Local Development

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Tailwind CSS
npm install
npm run build:css        # build once
npm run watch:css        # watch during development

# Environment
cp .env-sample .env      # then fill in real values

# Run
python manage.py migrate
python manage.py runserver
```

## Deployment

See [PI_DEPLOY.md](PI_DEPLOY.md) for full instructions (Orange Pi / Raspberry Pi):

- Gunicorn systemd service
- Nginx reverse proxy
- Cloudflare Tunnel
- CI/CD (GitHub Actions tests + `deploy.sh` / `auto-deploy.sh` on the Pi)
