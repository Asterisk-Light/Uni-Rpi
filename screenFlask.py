# app.py
# pip install flask aiortc opencv-python mss av

import asyncio
import json
import cv2
import numpy as np
import mss

from flask import Flask, request, jsonify, render_template
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from av import VideoFrame

app = Flask(__name__)

pcs = set()

# Screen capture track
class ScreenTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        img = np.array(self.sct.grab(self.monitor))
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        frame = VideoFrame.from_ndarray(img, format="bgr24")
        frame.pts = pts
        frame.time_base = time_base
        return frame

# Main arena page
@app.route("/")
def arena():
    return render_template("screenFlaskHTML.html")

# WebRTC offer endpoint
@app.route("/offer", methods=["POST"])
async def offer():
    params = request.json
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)

    track = ScreenTrack()
    pc.addTransceiver(track, direction="sendonly")

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return jsonify({
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)