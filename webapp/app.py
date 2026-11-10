"""Validators Hub - web UI on top of the `validators` library (System Under Test for Phase 2).

Data lives in memory; POST /reset restores a clean state so automated tests stay independent.
"""
import copy, csv, io, os, re
from datetime import datetime
from functools import wraps

import validators
from flask import Flask, Response, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-secret")

DEFAULT_USERS = {"student": {"pw": "Test@123", "email": "student@example.com"},
                 "admin": {"pw": "Admin@123", "email": "admin@example.com"}}
USERS, HISTORY, REGISTERED = copy.deepcopy(DEFAULT_USERS), {}, []
USERNAME_RE = re.compile(r"^[A-Za-z0-9._]{3,20}$")


def find_user(identifier):
    """Look a user up by username OR email (case-insensitive)."""
    ident = identifier.strip().lower()
    for uname, u in USERS.items():
        if ident in (uname.lower(), u["email"].lower()):
            return uname, u
    return None, None
COUNTRIES = ["Pakistan", "United States", "United Kingdom", "Germany", "Canada"]

# name, category, label, description, valid example, invalid example
_R = [
    ("email", "Network", "Email address", "Checks username, @ sign and domain rules.", "a@b.com", "nope"),
    ("url", "Network", "URL", "Scheme, host, port and path of a web link.", "https://example.com", "htp:/x"),
    ("domain", "Network", "Domain name", "Labels, length and allowed characters.", "example.com", "-bad.com"),
    ("hostname", "Network", "Hostname", "A host name or IP address.", "my-host.local", "bad host"),
    ("ipv4", "Network", "IPv4 address", "Four octets between 0 and 255.", "192.168.1.1", "256.1.1.1"),
    ("ipv6", "Network", "IPv6 address", "Eight hex groups, with :: shortening.", "::1", "12345::"),
    ("mac_address", "Network", "MAC address", "Six hex pairs separated by : or -.", "01:23:45:67:89:ab", "01:23:45"),
    ("slug", "Text", "URL slug", "Lowercase letters, numbers and single hyphens.", "my-post", "Bad Slug"),
    ("uuid", "Text", "UUID", "A version-4 universally unique identifier.", "2bc1c94f-0deb-43e9-92a1-4775189ec9f8", "not-a-uuid"),
    ("cron", "Text", "Cron expression", "Five-field schedule such as */5 * * * *.", "*/5 * * * *", "61 * * * *"),
    ("md5", "Hashes", "MD5 hash", "32 hexadecimal characters.", "d41d8cd98f00b204e9800998ecf8427e", "xyz"),
    ("sha1", "Hashes", "SHA-1 hash", "40 hexadecimal characters.", "da39a3ee5e6b4b0d3255bfef95601890afd80709", "abc"),
    ("sha256", "Hashes", "SHA-256 hash", "64 hexadecimal characters.", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "abc"),
    ("base16", "Encoding", "Base16", "Hexadecimal encoded text.", "48656C6C6F", "ZZ"),
    ("base32", "Encoding", "Base32", "RFC 4648 base32 with padding.", "JBSWY3DPEBLW64TMMQ======", "hello1"),
    ("base64", "Encoding", "Base64", "Base64 encoded text.", "SGVsbG8gV29ybGQ=", "Hello!"),
    ("card_number", "Payments", "Card number", "Any major card, with Luhn check.", "4242424242424242", "1234567890123456"),
    ("visa", "Payments", "Visa card", "Visa number format.", "4242424242424242", "5555555555554444"),
    ("mastercard", "Payments", "Mastercard", "Mastercard number format.", "5555555555554444", "4242424242424242"),
    ("iban", "Payments", "IBAN", "International bank account number.", "DE89370400440532013000", "DE00000000000000000000"),
    ("btc_address", "Crypto", "Bitcoin address", "Legacy and SegWit bitcoin addresses.", "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2", "abc"),
    ("country_code", "Regional", "Country code", "ISO 3166 country code.", "US", "XX"),
    ("currency", "Regional", "Currency code", "ISO 4217 currency code.", "USD", "ZZZ"),
]
REGISTRY = [dict(zip(("name", "cat", "label", "desc", "good", "bad"), r)) for r in _R]
META = {r["name"]: r for r in REGISTRY}
CATEGORIES = list(dict.fromkeys(r["cat"] for r in REGISTRY))


def login_required(view):
    @wraps(view)
    def wrapper(*a, **k):
        if "user" not in session:
            return redirect(url_for("login", next=request.path))
        return view(*a, **k)
    return wrapper


@app.get("/")
def index():
    return redirect(url_for("dashboard" if "user" in session else "login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        ident, pw = request.form.get("username", "").strip(), request.form.get("password", "")
        uname, u = find_user(ident)
        if not ident or not pw:
            error = "Username and password are required."
        elif not u or u["pw"] != pw:
            error = "Invalid username or password."
        else:
            session["user"] = uname          # the username is what the UI displays
            return redirect(request.args.get("next") or url_for("dashboard"))
    return render_template("login.html", error=error)


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.get("/dashboard")
@login_required
def dashboard():
    items = HISTORY.get(session["user"], [])
    total, valid = len(items), sum(i["valid"] for i in items)
    stats = {"total": total, "valid": valid, "invalid": total - valid,
             "rate": round(valid * 100 / total) if total else 0}
    top = {}
    for i in items:
        top[i["kind"]] = top.get(i["kind"], 0) + 1
    top = sorted(top.items(), key=lambda kv: -kv[1])[:4]
    return render_template("dashboard.html", stats=stats, top=top, recent=items[:5], meta=META)


@app.route("/validate", methods=["GET", "POST"])
@login_required
def validate():
    result, error, value = None, None, ""
    kind = request.values.get("kind", "email")
    kind = kind if kind in META else "email"
    if request.method == "POST":
        value = request.form.get("value", "").strip()
        if not value:
            error = "Please enter a value to validate."
        else:
            ok = getattr(validators, kind)(value) is True
            HISTORY.setdefault(session["user"], []).insert(0, {
                "kind": kind, "value": value, "valid": ok, "time": datetime.now().strftime("%H:%M:%S")})
            result = {"valid": ok, "kind": kind, "value": value}
    groups = {c: [r for r in REGISTRY if r["cat"] == c] for c in CATEGORIES}
    return render_template("validate.html", result=result, error=error, kind=kind, value=value,
                           groups=groups, meta=META)


@app.get("/catalog")
@login_required
def catalog():
    q, cat = request.args.get("q", "").strip().lower(), request.args.get("cat", "all")
    rows = [r for r in REGISTRY if (cat in ("all", "") or r["cat"] == cat)
            and (not q or q in r["name"] or q in r["label"].lower() or q in r["desc"].lower())]
    return render_template("catalog.html", rows=rows, q=q, cat=cat, categories=CATEGORIES, total=len(REGISTRY))


def _filtered_history():
    q, status = request.args.get("q", "").strip().lower(), request.args.get("status", "all")
    rows = HISTORY.get(session["user"], [])
    if q:
        rows = [r for r in rows if q in r["value"].lower() or q in r["kind"]]
    if status in ("valid", "invalid"):
        rows = [r for r in rows if r["valid"] == (status == "valid")]
    return rows, q, status


@app.get("/history")
@login_required
def history():
    rows, q, status = _filtered_history()
    return render_template("history.html", rows=rows, q=q, status=status, meta=META)


@app.get("/history/export")
@login_required
def export_history():
    rows, _, _ = _filtered_history()
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["time", "type", "value", "result"])
    for r in rows:
        w.writerow([r["time"], r["kind"], r["value"], "valid" if r["valid"] else "invalid"])
    return Response(out.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=history.csv"})


@app.post("/history/clear")
@login_required
def clear_history():
    HISTORY[session["user"]] = []
    return redirect(url_for("history"))


@app.route("/register", methods=["GET", "POST"])
def register():
    form, errors = {}, {}
    if request.method == "POST":
        form = request.form.to_dict()
        name, email = form.get("name", "").strip(), form.get("email", "").strip()
        username = form.get("username", "").strip()
        pw, confirm = form.get("password", ""), form.get("confirm", "")
        if len(name) < 2:
            errors["name"] = "Name must be at least 2 characters."
        if not USERNAME_RE.match(username):
            errors["username"] = "Username must be 3-20 characters: letters, numbers, dots or underscores."
        elif find_user(username)[0]:
            errors["username"] = "This username is already taken."
        if not email:
            errors["email"] = "Email is required."
        elif validators.email(email) is not True:
            errors["email"] = "Enter a valid email address."
        elif any(u["email"].lower() == email.lower() for u in USERS.values()):
            errors["email"] = "This email is already registered."
        if len(pw) < 8 or not any(c.isdigit() for c in pw):
            errors["password"] = "Password needs 8+ characters and a number."
        if pw != confirm:
            errors["confirm"] = "Passwords do not match."
        if form.get("country") not in COUNTRIES:
            errors["country"] = "Please choose a country."
        if not form.get("terms"):
            errors["terms"] = "You must accept the terms."
        if not errors:
            REGISTERED.append({"name": name, "username": username, "email": email, "country": form["country"]})
            USERS[username] = {"pw": pw, "email": email}
            return render_template("register_success.html", name=name, username=username, email=email)
    return render_template("register.html", form=form, errors=errors, countries=COUNTRIES)


@app.post("/reset")
def reset():
    """Test helper: restore the initial state."""
    USERS.clear(); USERS.update(copy.deepcopy(DEFAULT_USERS))
    HISTORY.clear(); REGISTERED.clear()
    return {"status": "reset"}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)), debug=False)
