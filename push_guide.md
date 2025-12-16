# How to Push Changes to GitHub

Before you can update your Raspberry Pi, you need to save your local changes to the GitHub repository.

## Option 1: Use the Helper Script (Windows)

1.  Open the folder: `d:\google antigravity\MIS PROJECT PRINTER FARM ERP\printfarm-erp`
2.  Double-click **`push_changes.bat`**.
3.  Enter a description of what you changed (e.g., "Added Gallery and Stress Tests").
4.  Wait for the success message.

## Option 2: Manual Command Line

1.  Open your terminal in the project folder.
2.  Run the following commands:

    ```bash
    # 1. Stage all changes
    git add .
    
    # 2. Commit with a message
    git commit -m "Your description here"
    
    # 3. Push to GitHub
    git push origin main
    ```

## Step 2: Update the Raspberry Pi

Once you see the "Success" message or `To github.com:...`, proceed to the **[Update Guide](update_guide.md)** to pull these changes onto your Raspberry Pi.
