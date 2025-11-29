# How to Update GitHub

Since you have made changes locally (Admin Panel, License, Bug Fixes), you need to push them to GitHub.

## Option 1: Using Terminal (Recommended)

Open your terminal (Command Prompt or PowerShell) in the project folder and run these commands one by one:

1.  **Check Status** (See what changed):
    ```bash
    git status
    ```

2.  **Add All Changes**:
    ```bash
    git add .
    ```

3.  **Commit Changes** (Save them with a message):
    ```bash
    git commit -m "Added Admin Panel, Fixed Bugs, and Updated License"
    ```

4.  **Push to GitHub**:
    ```bash
    git push origin main
    ```
    *(Note: If your branch is named `master`, use `git push origin master`)*

---

## Option 2: If this is a NEW Repository

If you haven't connected it to GitHub yet:

1.  Create a new repository on GitHub.com.
2.  Run these commands:
    ```bash
    git init
    git add .
    git commit -m "Initial commit"
    git branch -M main
    git remote add origin <YOUR_GITHUB_REPO_URL>
    git push -u origin main
    ```
