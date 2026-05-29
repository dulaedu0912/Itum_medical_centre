# Member Assignment

## Ranked by Lines of Code

| Rank | Member | Name | Feature | Lines | Files |
|------|--------|------|---------|:-----:|-------|
| 1 | Member 2 | Asintha | Registration | ~95 | `routes/register.py`, `templates/register.html` |
| 2 | Member 3 | Hashani | Login & Profile | ~115 | `routes/auth.py`, `templates/login.html`, `templates/profile.html` |
| 3 | Member 4 | Viduni | Edit Profile | ~115 | `routes/profile.py`, `templates/profile_edit.html`, `templates/change_password.html` |
| 4 | Member 1 | Kavindu | Foundation | ~140 | `app.py`, `db.py`, `routes/__init__.py`, `templates/base.html`, `templates/index.html`, `static/style.css`, `requirements.txt` |
| 5 | Member 7 | Ashan | Feedback | ~125 | `routes/feedback.py`, `templates/feedback_form.html`, `templates/feedback_list.html` |
| 6 | Member 6 | Neha | View & Cancel | ~135 | `routes/appointments.py`, `templates/appointments.html`, `templates/cancel.html` |
| 7 | Member 5 | Thejan | Book Appointment | ~140 | `routes/book.py`, `templates/book.html`, `templates/booking_confirmation.html` |
| 8 | Member 8 | Dulara | Admin Dashboard | ~165 | `routes/admin.py`, `templates/admin_dashboard.html`, `templates/admin_users.html`, `templates/admin_appointments.html` |

---

## Per-Member Breakdown

### Member 2 — Asintha — Registration

| | |
|---|---|
| **Lines** | ~95 |
| **Skills** | Variables, if/else, lists, functions |
| **Concepts** | Form validation, `.strip()`, `.lower()`, `list.append()` |
| **SQL** | One `INSERT`, one `SELECT` |
| **Files** | `routes/register.py`, `templates/register.html` |
| **Note** | All fields are explicit |
| **Assign to** | Asintha |

### Member 3 — Hashani — Login & Profile

| | |
|---|---|
| **Lines** | ~115 |
| **Skills** | Functions with `return`, if/elif, dict access |
| **Concepts** | `session['user_id']`, helper function, flash messages |
| **SQL** | One `SELECT` by email |
| **Files** | `routes/auth.py`, `templates/login.html`, `templates/profile.html` |
| **Note** | `get_logged_in_user()` helper is the only new pattern |
| **Assign to** | Hashani |

### Member 4 — Viduni — Edit Profile

| | |
|---|---|
| **Lines** | ~115 |
| **Skills** | Functions, if/else, basic SQL |
| **Concepts** | `UPDATE` SQL, `.strip()`, email uniqueness check (`AND id != ?`) |
| **SQL** | One `UPDATE`, one `SELECT` with exclusion |
| **Files** | `routes/profile.py`, `templates/profile_edit.html`, `templates/change_password.html` |
| **Note** | Forgetting `AND id != ?` causes false "email taken" errors |
| **Assign to** | Viduni |

### Member 1 — Kavindu — Foundation

| | |
|---|---|
| **Lines** | ~140 |
| **Skills** | Flask structure, SQLite, imports |
| **Concepts** | `Flask(__name__)`, blueprint registration, `render_template`, `CREATE TABLE`, loops over dicts, `generate_password_hash()` |
| **SQL** | 4 `CREATE TABLE`, seed `INSERT` for 3 doctors + 1 admin + 1 student |
| **Files** | `app.py`, `db.py`, `routes/__init__.py`, `templates/base.html`, `templates/index.html`, `static/style.css`, `requirements.txt` |
| **Note** | Everyone depends on this — a bug blocks all 7 others. |
| **Assign to** | Kavindu |

### Member 7 — Ashan — Feedback

| | |
|---|---|
| **Lines** | ~125 |
| **Skills** | Forms + basic DB queries |
| **Concepts** | `int()` conversion, `try/except ValueError`, aggregate SQL (`AVG`, `COUNT`, `GROUP BY`), `ROUND()` |
| **SQL** | One `INSERT`, one `SELECT` with JOIN, one aggregate `SELECT` with GROUP BY |
| **Files** | `routes/feedback.py`, `templates/feedback_form.html`, `templates/feedback_list.html` |
| **Note** | The `AVG` + `GROUP BY` query is the only tricky part |
| **Assign to** | Ashan |

### Member 6 — Neha — View & Cancel

| | |
|---|---|
| **Lines** | ~135 |
| **Skills** | Dynamic SQL + URL parameters |
| **Concepts** | `if/elif/else` with different query strings, `request.args.get('filter')`, ownership check (`WHERE student_id = ?`), URL parameter `<int:appt_id>` |
| **SQL** | Dynamic `SELECT` with filter conditions, `UPDATE` for cancel |
| **Files** | `routes/appointments.py`, `templates/appointments.html`, `templates/cancel.html` |
| **Note** | Dynamic query construction requires attention |
| **Assign to** | Neha |

### Member 5 — Thejan — Book Appointment

| | |
|---|---|
| **Lines** | ~140 |
| **Skills** | Solid Python, date comparison, multi-table JOIN |
| **Concepts** | `datetime.date.today()`, date string comparison, 3-table JOIN, double-booking detection (`status != 'cancelled'`), `last_insert_rowid()` |
| **SQL** | One `INSERT`, two `SELECT` (doctor validation + double-booking check), one JOIN query |
| **Files** | `routes/book.py`, `templates/book.html`, `templates/booking_confirmation.html` |
| **Note** | Double-booking logic and date comparison require careful attention |
| **Assign to** | Thejan |

### Member 8 — Dulara — Admin Dashboard

| | |
|---|---|
| **Lines** | ~165 |
| **Skills** | Most code, most SQL variety, comfortable with loops + dicts |
| **Concepts** | `COUNT(*)`, loop over status list, `LIKE` search, role-based access, 4 route functions |
| **SQL** | 4 aggregate queries, `LIKE` search, 3-table JOIN with LIMIT |
| **Files** | `routes/admin.py`, `templates/admin_dashboard.html`, `templates/admin_users.html`, `templates/admin_appointments.html` |
| **Note** | More volume than other features — most code and most SQL variety |
| **Assign to** | Dulara |

---

## Recommended Team Layout

| Person | Assign Member | Files | Why |
|--------|:------------:|-------|------|
| **Kavindu (leader)** | **Member 1** | `app.py`, `db.py`, `base.html`, `index.html`, `style.css`, `requirements.txt` | Foundation — owns the repo, pushes first, unblocks everyone. |
| Asintha | Member 2 | `routes/register.py`, `templates/register.html` | Registration — 95 lines, pure if/else, no SQL joins |
| Hashani | Member 3 | `routes/auth.py`, `templates/login.html`, `templates/profile.html` | Login & Profile — helper function is the only new concept |
| Viduni | Member 4 | `routes/profile.py`, `templates/profile_edit.html`, `templates/change_password.html` | Edit Profile — UPDATE + edge cases |
| Ashan | Member 7 | `routes/feedback.py`, `templates/feedback_form.html`, `templates/feedback_list.html` | Feedback — GROUP BY comfort |
| Neha | Member 6 | `routes/appointments.py`, `templates/appointments.html`, `templates/cancel.html` | View & Cancel — dynamic queries + ownership check |
| Thejan | Member 5 | `routes/book.py`, `templates/book.html`, `templates/booking_confirmation.html` | Book Appointment — date logic + 3-table JOIN |
| Dulara | Member 8 | `routes/admin.py`, `templates/admin_dashboard.html`, `templates/admin_users.html`, `templates/admin_appointments.html` | Admin Dashboard — most code + most SQL variety |

---

Share this with your team so everyone knows what to expect!
