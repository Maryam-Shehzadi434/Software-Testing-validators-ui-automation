# Validators Hub (web UI) - System Under Test

Flask web app on top of the `validators` library. Used as the target for the Phase 2
Playwright + BDD automation framework.

Run: `pip install -r requirements.txt` then `python webapp/app.py` (http://127.0.0.1:5000)
Accounts: student / Test@123, admin / Admin@123. New users register with a username and can sign in with the username OR the email. The UI always shows the username.

| Page | URL | Highlights |
|------|-----|-----------|
| Login | /login | validation errors, redirect when logged out |
| Register | /register | name, username, email, password (+strength meter), dropdown, checkbox, up to 7 error messages |
| Dashboard | /dashboard | counters, pass-rate donut, top validators, recent activity |
| Validate | /validate | 23 validators, example chips, instant verdict (Scenario Outline friendly) |
| Catalog | /catalog | search + category filter, "Try it" links |
| History | /history | search, status filter, CSV export (download testing), clear |

Test hooks: every element has a `data-testid`; `POST /reset` restores state; `GET /health` for CI.
Light, elegant theme with the Vali mascot; port is set with the `PORT` env variable.
