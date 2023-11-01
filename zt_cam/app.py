from flask import Flask, render_template, jsonify, Response
import subprocess
from picamera import PiCamera
import io
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

base_url = "http://192.168.8.1" #web ui for modem
target_ip = "192.168.192.250" #ip address (assigned by zt) of the control device

camera = PiCamera()
camera.rotation = 0
camera.resolution = (640, 480)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def status():
    result = subprocess.run(['sudo', 'zerotier-cli', 'peers'], capture_output=True, text=True).stdout
    lines = result.split('\n')[1:]

    leaf_direct = any('LEAF' in line and 'DIRECT' in line for line in lines)
    leaf_relayed = any('LEAF' in line and 'RELAYED' in line for line in lines)

    if leaf_direct and leaf_relayed:
        return jsonify(status='MIXED')
    elif leaf_direct:
        return jsonify(status='DIRECT')
    elif leaf_relayed:
        return jsonify(status='RELAYED')
    else:
        return jsonify(status='ERROR')

@app.route("/get_signal")
def get_signal():
    session = requests.Session()

    # Try with huawei first (tested with e3372h and e8372h)
    session.get(base_url + "/html/home.html")
    url_old = base_url + "/api/monitoring/status"
    response_old = session.get(url_old)

    if response_old.status_code == 200:
        root = ET.fromstring(response_old.content)
        signal_icon_value = root.find('SignalIcon').text
        session.close()
        return jsonify({"signal": signal_icon_value})

    # If the old modem's URL fails, try the fake e3372h-510 from ali express XD
    else:
        session.get(base_url + "/index.html")
        url_new = base_url + "/reqproc/proc_get"
        response_new = session.get(
            url_new,
            params={
                "multi_data": "1",
                "isTest": "false",
                "sms_received_flag_flag": "0",
                "sts_received_flag_flag": "0",
                "cmd": "signalbar",
                "_": "1698755936405"
            }
        )
        if response_new.status_code == 200:
            data = response_new.json()
            signalbar_value = data.get('signalbar')
            session.close()
            return jsonify({"signal": signalbar_value})

    session.close()
    return jsonify({"error": "Unable to get signal"}), 500

@app.route('/latency')
def latency():
    def get_latency(target_ip):
        result = subprocess.run(['ping', '-c', '3', target_ip], capture_output=True, text=True).stdout
        for line in result.split('\n'):
            if "rtt min/avg/max/mdev" in line:
                latency = line.split('/')[4]
                return int(float(latency))
        return None

    avg_latency = get_latency(target_ip)

    if avg_latency is not None:
        return jsonify(latency=avg_latency)
    else:
        return jsonify(error="Could not determine latency"), 500
        
def gen():
    while True:
        stream = io.BytesIO()
        camera.capture(stream, 'jpeg')
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + stream.getvalue() + b'\r\n\r\n')
        stream.seek(0)
        stream.truncate()

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=6789)
    except KeyboardInterrupt:
        pass
    finally:
        camera.close()
        