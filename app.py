from flask import Flask, request, jsonify
import requests
import subprocess

app = Flask(__name__)

streams = {}

def start_ffmpeg(rtsp_url, rtp_port):
    command = [
        'ffmpeg',
        '-i', rtsp_url,
        '-f', 'rtp',
        f'rtp://localhost:{rtp_port}'
    ]
    return subprocess.Popen(command)

def send_offer_to_janus(sdp_offer):
    janus_url = 'http://localhost:8088/janus'
    response = requests.post(janus_url, json={"type": "offer", "sdp": sdp_offer})
    return response.json()

@app.route('/api/add_camera', methods=['POST'])
def add_camera():
    data = request.json
    rtsp_url = data['rtsp_url']
    rtp_port = data['rtp_port']
    process = start_ffmpeg(rtsp_url, rtp_port)
    streams[rtsp_url] = process

    return jsonify({"message": "Camera added successfully"}), 201

@app.route('/api/stop_camera', methods=['POST'])
def stop_camera():
    data = request.json
    rtsp_url = data['rtsp_url']

    # Stop the FFmpeg process
    if rtsp_url in streams:
        streams[rtsp_url].terminate()
        del streams[rtsp_url]

    return jsonify({"message": "Camera stopped successfully"}), 200

@app.route('/api/webrtc_offer', methods=['POST'])
def webrtc_offer():
    sdp_offer = request.json['sdp']

    # Pass the offer to Janus (or handle SDP exchange directly)
    # Example request to Janus:
    janus_response = send_offer_to_janus(sdp_offer)

    return jsonify(janus_response['sdp'])