# Raspberry Pi 4B Setup Guide (Ubuntu Server LTS)

This guide covers setting up a Raspberry Pi 4B (4GB/8GB) from scratch with **Ubuntu Server LTS** to run the Print Farm ERP in a headless configuration (no monitor/keyboard).

## Phase 1: Flashing the OS

You will need:
- A microSD card (16GB+ recommended).
- A computer with an SD card reader.
- **Raspberry Pi Imager** (Download from [raspberrypi.com/software](https://www.raspberrypi.com/software/)).

1.  **Open Raspberry Pi Imager**.
2.  **Choose OS**:
    - Click "Choose OS" -> "Other General-Purpose OS" -> "Ubuntu".
    - Select **Ubuntu Server 24.04 LTS (64-bit)** (or 22.04 LTS). *Do not choose Desktop.*
3.  **Choose Storage**: Select your SD card.
4.  **Advanced Options (The Gear Icon)** - *Critical for Headless Setup*:
    - Click "Next", and when asked "Would you like to apply OS customisation settings?", select **EDIT SETTINGS**.
    - **General Tab**:
        - **Set hostname**: `printfarm-pi` (or whatever you prefer).
        - **Set username and password**: e.g., `ubuntu` / `yourpassword`.
        - **Configure Wireless LAN**: Enter your WiFi SSID and Password. Set Country Code (e.g., US, IN, GB).
    - **Services Tab**:
        - **Enable SSH**: Check this box. Select "Use password authentication".
5.  **Write**: Click SAVE and then YES to flash the card.

## Phase 2: First Boot & Connection

1.  Insert the SD card into the Raspberry Pi.
2.  Power on the Pi.
3.  Wait 2-3 minutes for the first boot.
4.  **Find IP Address**: Check your router's client list for `printfarm-pi` or use a network scanner app on your phone.
5.  **SSH into the Pi**:
    - Windows (Command Prompt): `ssh ubuntu@<ip-address>`
    - Mac/Linux: `ssh ubuntu@<ip-address>`
    - Enter your password when prompted.

## Phase 3: Server Preparation

Once logged in via SSH:

1.  **Update System**:
    ```bash
    sudo apt update
    sudo apt upgrade -y
    ```
2.  **Install Dependencies**:
    ```bash
    sudo apt install -y python3-pip python3-venv git
    ```

## Phase 4: Deploying the Application

1.  **Clone the Repository**:
    ```bash
    git clone <YOUR_GITHUB_REPO_URL> printfarm-erp
    # If you haven't pushed it yet, you can transfer files via SCP:
    # scp -r path/to/printfarm-erp ubuntu@<ip-address>:~/
    ```
2.  **Enter the Directory**:
    ```bash
    cd printfarm-erp
    ```
3.  **Create Virtual Environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
4.  **Install Python Libraries**:
    ```bash
    pip install -r requirements.txt
    pip install waitress  # Production server
    ```
5.  **Setup Environment**:
    ```bash
    cp .env.example .env  # Or create one manually
    nano .env
    # Edit DATABASE_URL and SECRET_KEY
    ```
6.  **Initialize Database**:
    ```bash
    export FLASK_APP=wsgi.py
    python3 scripts/init_db.py
    python3 scripts/seed_demo_data.py
    ```

## Phase 5: Running as a Service (Auto-start)

To keep the server running after you disconnect SSH, create a systemd service.

1.  **Create Service File**:
    ```bash
    sudo nano /etc/systemd/system/printfarm.service
    ```
2.  **Paste Configuration** (Adjust paths/user if needed):
    ```ini
    [Unit]
    Description=PrintFarm ERP Waitress Server
    After=network.target

    [Service]
    User=ubuntu
    WorkingDirectory=/home/ubuntu/printfarm-erp
    Environment="PATH=/home/ubuntu/printfarm-erp/venv/bin"
    ExecStart=/home/ubuntu/printfarm-erp/venv/bin/waitress-serve --listen=*:8080 wsgi:app
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```
3.  **Start and Enable**:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl start printfarm
    sudo systemctl enable printfarm
    ```
4.  **Check Status**:
    ```bash
    sudo systemctl status printfarm
    ```

## Phase 6: Accessing

- **Local Network**: `http://<pi-ip-address>:8080`
- **Internet**: Follow the **Deployment Guide** to set up DuckDNS and port forwarding to your Pi's IP.
