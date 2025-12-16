# Updating Your PrintFarm ERP Deployment

This guide explains how to update your Raspberry Pi deployment with the latest code from GitHub.

**Repository**: `https://github.com/proplayerplayz/printfarm-erp`

## Step 1: Connect to the Raspberry Pi
Open your terminal (or Command Prompt) and SSH into your Pi.
```bash
ssh ubuntu@<your-pi-ip-address>
```
*(Enter password when prompted)*

## Step 2: Navigate to the Project Directory
Go to the folder where the application is installed.
```bash
cd ~/printfarm-erp
```

## Step 3: Fetch the Latest Code
Download the latest changes from GitHub.

**Option A: Standard Pull (Safest)**
Use this if you haven't modified files directly on the Pi.
```bash
git pull origin main
```
*Note: If it asks for credentials, you may need to enter your GitHub username/token, or if it says "fast-forward", it worked.*

**Option B: Force Update (Overwrites Pi Changes)**
Use this if you get "merge conflict" errors and just want the Pi to match GitHub exactly.
```bash
git fetch --all
git reset --hard origin/main
```

## Step 4: Update Dependencies
If the update included new libraries (e.g., usually indicated by a change in `requirements.txt`), install them.
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Step 5: Update the Database
If the update included changes to the database structure (new tables or columns), apply the migrations.
```bash
export FLASK_APP=wsgi.py
flask db upgrade
```
*If this fails saying "flask not found", make sure you ran the `source venv/bin/activate` command in Step 4.*

## Step 6: Restart the Application
Restart the background service to load the new Python code.
```bash
sudo systemctl restart printfarm
```

## Step 7: Verify
Check that the service is running correctly.
```bash
sudo systemctl status printfarm
```
If it says `Active: active (running)`, you are done! Visit your site in the browser to confirm the new features are visible.
