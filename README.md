# Raspberry Pi Print Farm ERP / MIS

A lightweight, role-based ERP system for managing a 3D printing farm. Built with Flask, SQLAlchemy, MariaDB, and Bootstrap 5. Designed to run on Raspberry Pi OS Lite.

## Features

- **Public Customer Portal**: Customers can upload STLs, get instant estimates, and track orders.
- **Operator Portal**: Kanban-style job queue, printer status management, and job tracking.
- **Ops Manager Portal**: Inventory management (filament/parts), shipment processing, and reorder suggestions.
- **Admin Portal**: User management, audit logs, and system configuration.
- **Security**: Role-based access control, secure file uploads, and Nginx LAN restriction configurations.

## Tech Stack

- **Backend**: Python 3.x, Flask, SQLAlchemy, PyMySQL
- **Database**: MariaDB / MySQL
- **Frontend**: Jinja2 Templates, Bootstrap 5
- **Server**: Gunicorn + Nginx + Systemd

## Installation

### 1. System Requirements
- Raspberry Pi (3B+ or 4 recommended) running Raspberry Pi OS Lite (64-bit).
- Python 3.9+
- MariaDB Server

### 2. Initial Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv mariadb-server libmariadb-dev-compat nginx git

# Clone repository
git clone https://github.com/yourusername/printfarm-erp.git
cd printfarm-erp
```

### 3. Database Setup

```bash
sudo mysql -u root
```

```sql
CREATE DATABASE printfarm_db;
CREATE USER 'printuser'@'localhost' IDENTIFIED BY 'yourpassword';
GRANT ALL PRIVILEGES ON printfarm_db.* TO 'printuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 4. Application Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Configure Environment
cp .env.example .env
nano .env
# Edit DATABASE_URL to: mysql+pymysql://printuser:yourpassword@localhost/printfarm_db
```

### 5. Initialize & Seed

```bash
# Initialize Tables
python scripts/init_db.py

# Seed Demo Data (Printers, Filament, Demo Customer)
python scripts/seed_demo_data.py

# Create your Admin User
python scripts/create_admin.py "Admin User" "admin@example.com" "securepassword"
```

## Running the Application

### Development (Local)

```bash
export FLASK_APP=wsgi.py
export FLASK_DEBUG=1
flask run --host=0.0.0.0
```
Visit `http://localhost:5000`

### Production (Systemd + Nginx)

1. **Test Gunicorn**:
   ```bash
   gunicorn --bind 0.0.0.0:8000 wsgi:app
   ```

2. **Setup Systemd Service**:
   ```bash
   sudo cp systemd/printfarm-erp.service /etc/systemd/system/
   sudo nano /etc/systemd/system/printfarm-erp.service
   # Verify paths and user (default is 'pi')
   
   sudo systemctl start printfarm-erp
   sudo systemctl enable printfarm-erp
   ```

3. **Setup Nginx**:
   ```bash
   sudo cp nginx/public_customer_only.conf /etc/nginx/sites-available/printfarm
   sudo ln -s /etc/nginx/sites-available/printfarm /etc/nginx/sites-enabled/
   sudo rm /etc/nginx/sites-enabled/default
   sudo nginx -t
   sudo systemctl restart nginx
   ```

## Demo Walkthrough

1. **Customer Flow**:
   - Go to `/customer/home`.
   - Register a new account.
   - Click "New Order", upload an `.stl` file.
   - See estimated price and submit.
   - View order status in "My Orders".

2. **Operator Flow**:
   - Log in as Operator (or use Admin account).
   - Go to `/operator/jobs`.
   - See "Waiting" jobs. Assign to a printer.
   - Go to `/operator/dashboard` to see active printers.
   - Mark job as "Done" when finished.

3. **Ops Flow**:
   - Log in as Ops Manager.
   - Go to `/ops/shipments`.
   - See completed order. Enter tracking number and "Ship".
   - Go to `/ops/inventory/filament` to update stock.

4. **Admin Flow**:
   - Log in as Admin.
   - Go to `/admin/users` to manage staff.
   - Go to `/admin/audit` to see who did what.
