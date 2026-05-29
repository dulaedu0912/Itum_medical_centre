# How to Run This Project on Your Computer

## Prerequisites

| Software | Where to Get It | How to Verify |
|----------|----------------|---------------|
| **Python 3.10+** | https://www.python.org/downloads/ | `python --version` |
| **Git** | https://git-scm.com/download/win | `git --version` |
| **VS Code (optional)** | https://code.visualstudio.com/ | `code --version` |

> **IMPORTANT:** When installing Python, check **"Add Python to PATH"** before clicking Install.

---

## Step 1 — Clone the Repository

The group leader will give you the GitHub repository URL. Then:

```powershell
cd C:\Users\%USERNAME%\Documents
git clone https://github.com/YOUR_USERNAME/itum_clinic.git
cd itum_clinic
```

---

## Step 2 — Create Virtual Environment

```powershell
python -m venv venv
```

Then activate it:

```powershell
venv\Scripts\activate
```

You should see `(venv)` appear at the beginning of your terminal prompt.

---

## Step 3 — Install Flask

```powershell
pip install flask
```

To verify:

```powershell
pip list
```

You should see `flask` in the output.

---

## Step 4 — Run the Project

```powershell
python app.py
```

Open your browser and go to: **http://127.0.0.1:5000**

You should see the ITUM Medical Centre home page.

---

## Step 5 — Test All Features

Open a **second** terminal (keep the first one running the app) and run:

```powershell
cd C:\Users\%USERNAME%\Documents\itum_clinic
venv\Scripts\activate
python -m pip install pytest
python -m pytest test_all.py -v
```

All 72 tests should pass with green `PASSED` markers.

---

## Quick Reference (Every Time After Setup)

```powershell
cd C:\Users\%USERNAME%\Documents\itum_clinic
venv\Scripts\activate
python app.py
```

Open http://127.0.0.1:5000

## Login Credentials for Testing

### Admin Account
Use this to access the dashboard and manage everything:

| Email | Password | Role |
|-------|----------|------|
| `admin@itum.lk` | `admin123` | Admin |

### Doctor Accounts
Each doctor has a login to view all appointments on the dashboard:

| Email | Password | Doctor |
|-------|----------|--------|
| `priya@itum.lk` | `doctor123` | Dr. Priya Mendis |
| `kasun@itum.lk` | `doctor123` | Dr. Kasun Silva |
| `nimal@itum.lk` | `doctor123` | Dr. Nimal Perera |

### Student Account
Use this to test booking appointments and feedback:

| Email | Password | Name |
|-------|----------|------|
| `student@itum.lk` | `student123` | Test Student |

You can also register a new account at http://127.0.0.1:5000/auth/register.

---

## Default Admin Login (Reference)

| Email | Password | Role |
|-------|----------|------|
| `admin@itum.lk` | `admin123` | Admin |

Use this to test the admin dashboard features.

---

## Troubleshooting

### "python is not recognized"

Python is not in your PATH. Reinstall Python and check **"Add Python to PATH"**.

Or use the full path:
```powershell
C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\python app.py
```

### "No module named flask"

You forgot to activate the virtual environment:
```powershell
venv\Scripts\activate
pip install flask
```

### "Cannot activate virtual environment"

PowerShell blocks script execution. Run this once:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again.

### "Port 5000 already in use"

Another program is using port 5000. Either:
- Close the other program, or
- Change the port in `app.py` to `5001`:
  ```python
  app.run(debug=True, port=5001)
  ```

### "clinic.db file is broken or too large"

Delete the `clinic.db` file and restart the app. It will be recreated with fresh seed data.

```powershell
Remove-Item clinic.db
python app.py
```
