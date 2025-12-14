# GitHub Repository Setup Guide

Follow these steps to push your Print Farm ERP code to a new GitHub repository.

## 1. Create a Repository on GitHub

1.  Log in to [GitHub](https://github.com).
2.  Click the **+** icon (top right) -> **New repository**.
3.  **Repository name**: `printfarm-erp` (or your preferred name).
4.  **Public/Private**: Choose Private if you don't want the world to see your code yet.
5.  **Initialize**: Do **NOT** check "Add a README", ".gitignore", or "license". You want an empty repo.
6.  Click **Create repository**.
7.  Copy the HTTPS URL provided (e.g., `https://github.com/YourUsername/printfarm-erp.git`).

## 2. Initialize Git Locally

Open your terminal (Command Prompt or PowerShell) in the project folder:

```bash
cd "d:\google antigravity\MIS PROJECT PRINTER FARM ERP\printfarm-erp"
```

Run the following commands one by one:

```bash
# Initialize a new git repo
git init

# Add all files (excluding ones in .gitignore)
git add .

# Commit the files
git commit -m "Initial commit of PrintFarm ERP"

# Rename the branch to main (standard practice)
git branch -M main

# Add the link to your GitHub repo (PASTE YOUR URL HERE)
git remote add origin https://github.com/YourUsername/printfarm-erp.git

# Push your code
git push -u origin main
```

## 3. Verify

Refresh your GitHub repository page. You should now see your files (`app/`, `scripts/`, `README.md`, etc.).

> [!NOTE]
> Because of the `.gitignore` file, your `printfarm.db`, `.env` file, and `venv` folder were NOT uploaded. This is correct and keeps your secrets safe.
> On the Raspberry Pi or other computers, you will create a new `.env` and run the setup scripts as described in `raspberry_pi_setup.md`.
