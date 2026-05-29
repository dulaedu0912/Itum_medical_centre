# Git Workflow for Team Project

## What is Git?

Git tracks changes to files so multiple people can work on the same project without overwriting each other's work. Think of it like Google Docs but for code — everyone edits their own copy, then merges changes together.

---

## Quick Command Reference

| When to Use | Command |
|-------------|---------|
| **First time** getting the project | `git clone <url>` |
| **Check** what branch you're on | `git branch` |
| **Create** a new branch | `git checkout -b feature/your-feature` |
| **See** what files you changed | `git status` |
| **See** exact changes in files | `git diff` |
| **Save** your changes locally | `git add -A` then `git commit -m "message"` |
| **Upload** your changes to GitHub | `git push -u origin feature/your-feature` |
| **Get** latest code from GitHub | `git pull` |
| **Switch** to another branch | `git checkout main` |

---

## Your Weekly Workflow (Step by Step)

### Day 1 — Get the Project

Run this **once**:

```powershell
cd C:\Users\%USERNAME%\Documents
git clone https://github.com/YOUR_USERNAME/itum_clinic.git
cd itum_clinic
```

### Day 2 — Create Your Feature Branch

```powershell
git checkout -b feature/your-feature-name
```

Example branch names:
- `feature/registration` (Member 2)
- `feature/auth` (Member 3)
- `feature/profile` (Member 4)
- `feature/book` (Member 5)
- `feature/appointments` (Member 6)
- `feature/feedback` (Member 7)
- `feature/admin` (Member 8)

You should now be on your own branch. Verify with:

```powershell
git branch
```

The active branch will have a `*` next to it.

### Every Day — Before You Start Coding

Get the latest changes from your team:

```powershell
git checkout main
git pull
git checkout feature/your-feature-name
git merge main
```

This brings any updates from your teammates into your feature branch.

### Every Day — After You Finish Coding

Save and upload your work:

```powershell
git status
git add -A
git commit -m "Describe what you did (e.g., Added registration form validation)"
git push -u origin feature/your-feature-name
```

> **Tip:** Write clear commit messages. Instead of `"fixed stuff"` write `"Added phone number field to registration form"`.

### End of Project — Create a Pull Request

When your feature is complete:

1. Go to your repository on GitHub (https://github.com/YOUR_USERNAME/itum_clinic)
2. Click **"Pull Requests"** → **"New Pull Request"**
3. Select your branch (`feature/your-feature-name`) → **main**
4. Click **"Create Pull Request"**
5. Add a description of what you built
6. Click **"Create Pull Request"**

The group leader will review and merge it.

### After Your PR is Merged

```powershell
git checkout main
git pull
```

Now delete your old branch (optional):

```powershell
git branch -d feature/your-feature-name
```

---

## Common Scenarios & How to Handle Them

### "I made changes but want to undo them"

```powershell
git checkout -- filename.py
```

This discards changes to `filename.py` and restores the last saved version.

### "I committed but want to undo the commit"

```powershell
git reset --soft HEAD~1
```

This undoes your last commit but keeps your changes in the file.

### "Git says 'push rejected'"

Someone else pushed before you. Pull their changes first:

```powershell
git pull origin main --rebase
git push
```

### "I accidentally made changes on main instead of my branch"

1. Save your changes temporarily:
   ```powershell
   git stash
   ```
2. Create and switch to your feature branch:
   ```powershell
   git checkout -b feature/your-feature
   ```
3. Restore your changes:
   ```powershell
   git stash pop
   ```

### "I want to see what my teammate is working on"

```powershell
git fetch
git checkout teammate-branch-name
```

This switches to their branch so you can see their code.

---

## Git Cheat Sheet

```
git clone <url>          Download the project for the first time
git branch               List all branches (* = current)
git checkout -b <name>   Create and switch to a new branch
git checkout <name>      Switch to an existing branch
git status               See what files have changed
git diff                 See the exact line-by-line changes
git add -A               Stage all changed files for commit
git commit -m "msg"      Save staged changes with a message
git push                 Upload commits to GitHub
git pull                 Download latest commits from GitHub
git merge <branch>       Merge another branch into your current one
git log --oneline        See recent commit history
```

---

## Do's and Don'ts

### ✅ DO

- **Always create a branch** before making changes. Never commit directly to `main`.
- **Pull before you push** — always run `git pull` before `git push`.
- **Write clear commit messages** — your teammates need to understand what you changed.
- **Commit often** — after each logical step, not once at the end.
- **Only change your own files** — each member owns specific files. Don't touch others'.

### ❌ DON'T

- **Don't edit files assigned to other members** — that causes merge conflicts.
- **Don't use `--force` push** — it overwrites other people's work.
- **Don't commit the `venv/` folder** — it's already in `.gitignore`.
- **Don't commit `clinic.db`** — it's already in `.gitignore`.
- **Don't panic** — almost everything in Git can be undone.
