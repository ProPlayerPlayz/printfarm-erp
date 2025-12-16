# Deployment Guide: PrintFarm ERP

This guide explains how to deploy the Print Farm ERP for remote access using **DuckDNS** (free dynamic DNS) and **Waitress** (Windows-compatible production server).

> [!WARNING]
> **Security Warning**: Exposing a local server to the internet carries risks. Ensure your `SECRET_KEY` in `.env` is strong and random in production. Do not use default passwords.

## 1. Prerequisites

- A computer running the ERP (Windows/Linux/Mac).
- Internet access with router admin privileges.
- **Internet Access**: Required for the Analytics Dashboard to load Chart.js from CDN.
- Python installed.

## 2. Setup DuckDNS

1.  Go to [duckdns.org](https://www.duckdns.org/).
2.  Sign in (Twitter, GitHub, etc.).
3.  Create a domain (e.g., `my-3d-farm.duckdns.org`).
4.  **Update IP**: Ensure the IP address matches your current public IP (DuckDNS usually detects this automatically).
5.  **Keep IP Updated**: Download the [DuckDNS Updater](https://www.duckdns.org/install.jsp) for your OS to keep your IP in sync if it changes.

## 3. Configure the ERP for Production

### Install Waitress
Flask's built-in server is not for production. Use `waitress`.

```bash
pip install waitress
```

### Create a Start Script
Create a file named `start_production.bat` (Windows) or `start_production.sh` (Linux) in the project root:

**start_production.bat**
```bat
@echo off
rem Ensure dependencies are installed
pip install waitress

rem Set production environment
set FLASK_APP=wsgi.py
set FLASK_DEBUG=0
rem Change this to a random string!
set SECRET_KEY=change-this-to-a-super-secret-random-string

echo Starting Waitress Server on 0.0.0.0:8080...
waitress-serve --listen=*:8080 wsgi:app
pause
```

## 4. Port Forwarding (Router Setup)

To let the internet reach your computer, you must forward a port on your router.

1.  **Find your Local IP**:
    - Windows: Open cmd, type `ipconfig`. Look for IPv4 Address (e.g., `192.168.1.15`).
2.  **Login to Router**:
    - Usually `http://192.168.1.1` or `http://192.168.0.1`.
3.  **Find Port Forwarding**:
    - Look for "Forwarding", "NAT", or "Virtual Server".
4.  **Add Rule**:
    - **Service Name**: PrintFarm
    - **External Port**: 80 (or 8080 if you want to use the same port outside)
    - **Internal Port**: 8080 (Matches the waitress script)
    - **Internal IP**: Your computer's local IP (`192.168.x.x`)
    - **Protocol**: TCP

> [!TIP]
> If your ISP blocks port 80, use a higher port like 8080 externally. You would then access your site via `http://my-3d-farm.duckdns.org:8080`.

## 5. Testing

1.  Run `start_production.bat`.
2.  On your phone (disconnect from WiFi to test external access), visit `http://my-3d-farm.duckdns.org` (or with port if specified).
3.  You should see your ERP login page.

## 6. Security Checklist for Online Deployment

- [ ] **Change Admin Password**: Ensure the admin user has a strong password.
- [ ] **Strong Secret Key**: Update `SECRET_KEY` in your start script.
- [ ] **HTTPS (Advanced)**: This guide uses HTTP. For secure encrypted traffic (highly recommended), consider setting up a reverse proxy like **Caddy** or **Nginx** which handles Let's Encrypt SSL certificates automatically.
    - *Simpler method*: Use **Tailscale** for private secure access without opening ports to the whole internet.
