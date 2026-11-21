from flask import Flask, render_template, request, jsonify, make_response
import os
import time
import hmac
import hashlib
import urllib.parse
import requests

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
app = Flask(__name__, template_folder=template_dir)

# ==========================================
# YAHAN APNA VPLINK DEVELOPER API TOKEN DAALEIN
# ==========================================
VPLINK_API_TOKEN = "696b1ae76598956d84ac9d914d6c68e0ccc1cc94"

ADMIN_PASS = "NORIX@2026"
SECRET_KEY = "norix_super_secret_hmac_key_change_if_needed"

KEYS_POOL = [
    "NORIX-1D-TK4B-SARY", "NORIX-1D-NC7H-XVQV", "NORIX-1D-9E7F-S5MQ", "NORIX-1D-AN78-U7MU",
    "NORIX-1D-HW9H-Y4EX", "NORIX-1D-93YL-DSFP", "NORIX-1D-9VKM-JK8R", "NORIX-1D-V7CB-SQJ3",
    "NORIX-1D-DZHD-52N3", "NORIX-1D-PVF8-DR6C", "NORIX-1D-Y9JT-Y386", "NORIX-1D-4A72-U7BF",
    "NORIX-1D-XBEF-BQD6", "NORIX-1D-K9T3-8FEQ", "NORIX-1D-K2F2-7S69", "NORIX-1D-B7S7-ENSM",
    "NORIX-1D-MURQ-LGAT", "NORIX-1D-3DJD-ZUY7", "NORIX-1D-JRDY-7YPZ", "NORIX-1D-K6CD-W4C9",
    "NORIX-1D-K6YP-DZDE", "NORIX-1D-5DQ3-8JU9", "NORIX-1D-9FRK-LCF9", "NORIX-1D-Z7HC-LRXB",
    "NORIX-1D-NCXC-FTV2", "NORIX-1D-E6MZ-NH33", "NORIX-1D-N2AG-NNZK", "NORIX-1D-EN5G-YM7Y",
    "NORIX-1D-XDVK-R98T", "NORIX-1D-EJHR-ZDYW", "NORIX-1D-NW9W-WY3A", "NORIX-1D-MLNV-SVPT",
    "NORIX-1D-GHP2-G46E", "NORIX-1D-HBWD-LCCC", "NORIX-1D-MCGP-VW6Z", "NORIX-1D-77DB-3KJM",
    "NORIX-1D-QJYF-QS38", "NORIX-1D-DYKP-CQCG", "NORIX-1D-TMJJ-W89F", "NORIX-1D-AJJ4-GDBT",
    "NORIX-1D-LNH6-JK8T", "NORIX-1D-BVLU-AEMA", "NORIX-1D-Q3XE-DMAL", "NORIX-1D-Y582-XZDX",
    "NORIX-1D-ATLA-563U", "NORIX-1D-DWUF-R5GR", "NORIX-1D-RNTN-MNPL", "NORIX-1D-62MV-Y5UZ",
    "NORIX-1D-HMNT-APPK", "NORIX-1D-R8TN-397C", "NORIX-1D-JS8C-BDLB", "NORIX-1D-4S6G-JQ6P",
    "NORIX-1D-FRM7-ZV4N", "NORIX-1D-RYY9-AYTD", "NORIX-1D-3RQC-SWFT", "NORIX-1D-CRH5-BQ7V",
    "NORIX-1D-5GMG-NMJ9", "NORIX-1D-XHJZ-QQPD", "NORIX-1D-7MNW-83UR", "NORIX-1D-QHSC-3DHC",
    "NORIX-1D-6XNK-HER7", "NORIX-1D-YS7L-LPX6", "NORIX-1D-S7RA-BQNK", "NORIX-1D-AU4Z-TVK6",
    "NORIX-1D-KSX3-Q8BG", "NORIX-1D-6KLN-P4K8", "NORIX-1D-SQJ5-2TYL", "NORIX-1D-FGDP-9A36",
    "NORIX-1D-ZV8L-B7RP", "NORIX-1D-N4RQ-AA4H", "NORIX-1D-7Y83-PN5G", "NORIX-1D-BE6C-FHVG",
    "NORIX-1D-7HT9-9HYJ", "NORIX-1D-W7SV-Z5AA", "NORIX-1D-3UGV-UXQ6", "NORIX-1D-3EKB-ZELE",
    "NORIX-1D-BTLB-YDM4", "NORIX-1D-3XS5-ACJE", "NORIX-1D-4N6Q-UUWC", "NORIX-1D-KMXC-EACX",
    "NORIX-1D-CK3G-TPTT", "NORIX-1D-U4UN-BPSP", "NORIX-1D-3NSV-HKFA", "NORIX-1D-HHST-7VDE",
    "NORIX-1D-EGZQ-D6BM", "NORIX-1D-9L4N-KV5E", "NORIX-1D-5QTZ-4R38", "NORIX-1D-XF83-NGDG",
    "NORIX-1D-NE8G-JTW9", "NORIX-1D-3LN4-MR9Y", "NORIX-1D-MR5E-BNYN", "NORIX-1D-S6VG-5A87",
    "NORIX-1D-ZDR6-8T6U", "NORIX-1D-Z877-DZ7G", "NORIX-1D-NCAU-3EZ3", "NORIX-1D-SWJ7-HQT3",
    "NORIX-1D-X593-X4PV", "NORIX-1D-D3EK-LCH4", "NORIX-1D-CGE3-MPB8", "NORIX-1D-4GMU-NGJJ"
]

claimed_ips = {}
used_keys = set()

def get_user_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or "unknown"

def make_verify_token(ip, ts):
    msg = f"{ip}:{ts}".encode()
    sig = hmac.new(SECRET_KEY.encode(), msg, hashlib.sha256).hexdigest()[:24]
    return f"{ts}.{sig}"

def check_verify_token(ip, token):
    if not token or "." not in token:
        return False
    try:
        ts_str, sig = token.split(".", 1)
        ts = int(ts_str)
        now = int(time.time())
        if now - ts > 1800 or now - ts < 5:
            return False
        expected = hmac.new(SECRET_KEY.encode(), f"{ip}:{ts}".encode(), hashlib.sha256).hexdigest()[:24]
        return hmac.compare_digest(sig, expected)
    except Exception:
        return False

@app.route('/')
def home():
    user_ip = get_user_ip()
    v_token = request.args.get('v', '')
    verified = check_verify_token(user_ip, v_token)
    return render_template('index.html', verified=verified, v_token=v_token)

@app.route('/api/create-link', methods=['POST'])
def create_link():
    if not VPLINK_API_TOKEN or "APNA_VPLINK" in VPLINK_API_TOKEN:
        return jsonify({"status": "error", "message": "VPLINK_API_TOKEN set nahi hai!"}), 500

    user_ip = get_user_ip()
    now = int(time.time())
    token = make_verify_token(user_ip, now)

    base_url = request.host_url.rstrip('/')
    dest_url = f"{base_url}/?v={token}"
    encoded_dest = urllib.parse.quote(dest_url, safe='')

    api_url = f"https://vplink.in/api?api={VPLINK_API_TOKEN}&url={encoded_dest}"
    try:
        r = requests.get(api_url, timeout=10).json()
        if r.get("status") == "success" and r.get("shortenedUrl"):
            return jsonify({"status": "success", "url": r["shortenedUrl"]})
        return jsonify({"status": "error", "message": r.get("message", "VPLink API error!")}), 400
    except Exception:
        return jsonify({"status": "error", "message": "VPLink server error."}), 500

@app.route('/api/get-key', methods=['POST'])
def get_key():
    data = request.get_json(silent=True) or {}
    user_ip = get_user_ip()
    v_token = data.get('v_token', '')

    if not check_verify_token(user_ip, v_token):
        return jsonify({"status": "error", "message": "Verification invalid ya expired!"}), 403

    now = int(time.time())
    day_seconds = 86400

    cookie_key = request.cookies.get('norix_daily_key')
    if cookie_key:
        return jsonify({"status": "already_claimed", "key": cookie_key, "message": "Key already active (24h limit)."})

    if user_ip in claimed_ips and (now - claimed_ips[user_ip]["time"] < day_seconds):
        return jsonify({"status": "already_claimed", "key": claimed_ips[user_ip]["key"], "message": "Key already claimed today."})

    day_bucket = now // day_seconds
    seed = int(hashlib.sha256(f"{user_ip}-{day_bucket}".encode()).hexdigest(), 16)

    assigned_key = None
    for offset in range(len(KEYS_POOL)):
        candidate = KEYS_POOL[(seed + offset) % len(KEYS_POOL)]
        if candidate not in used_keys:
            assigned_key = candidate
            break

    if not assigned_key:
        return jsonify({"status": "empty", "message": "No keys left today!"}), 404

    used_keys.add(assigned_key)
    claimed_ips[user_ip] = {"key": assigned_key, "time": now}

    resp = make_response(jsonify({
        "status": "success",
        "key": assigned_key,
        "message": "Access Granted! Valid for 24h."
    }))
    resp.set_cookie('norix_daily_key', assigned_key, max_age=day_seconds, httponly=True, samesite='Lax')
    return resp

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

@app.route('/api/admin/stats', methods=['POST'])
def admin_stats():
    data = request.get_json(silent=True) or {}
    if data.get('password') != ADMIN_PASS:
        return jsonify({"status": "error", "message": "Galat Password!"}), 401
    total = len(KEYS_POOL)
    used = len(used_keys)
    return jsonify({"status": "success", "total": total, "unused": total - used, "used": used})

@app.route('/api/admin/upload', methods=['POST'])
def admin_upload():
    data = request.get_json(silent=True) or {}
    if data.get('password') != ADMIN_PASS:
        return jsonify({"status": "error", "message": "Galat Password!"}), 401
    raw = data.get('keys', '')
    added = 0
    for line in raw.splitlines():
        k = line.strip()
        if k and k not in KEYS_POOL:
            KEYS_POOL.append(k)
            added += 1
    return jsonify({"status": "success", "message": f"{added} nayi keys add ho gayi!"})

@app.route('/api/admin/clear-used', methods=['POST'])
def admin_clear_used():
    data = request.get_json(silent=True) or {}
    if data.get('password') != ADMIN_PASS:
        return jsonify({"status": "error", "message": "Galat Password!"}), 401
    used_keys.clear()
    claimed_ips.clear()
    return jsonify({"status": "success", "message": "Used history reset ho gayi!"})
