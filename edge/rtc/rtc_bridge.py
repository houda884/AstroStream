import json
import numpy as np
from aiortc import RTCPeerConnection, VideoStreamTrack
from av import VideoFrame


class GameVideoTrack(VideoStreamTrack):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        frame = self.engine.get_frame()
        frame = np.ascontiguousarray(frame, dtype=np.uint8)

        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        video_frame = video_frame.reformat(format="yuv420p")
        video_frame.pts = pts
        video_frame.time_base = time_base
        return video_frame


class EdgeRTCBridge:
    def __init__(self, engine, detections_callback):
        self.engine = engine
        self.pc = RTCPeerConnection()
        self.channel = None
        self.detections_callback = detections_callback

        self.pc.addTrack(GameVideoTrack(engine))

        self.channel = self.pc.createDataChannel("data")
        print("✅ DataChannel créé côté edge")

        @self.channel.on("open")
        def on_open():
            print("✅ DataChannel ouvert côté edge")

        @self.channel.on("close")
        def on_close():
            print("⚠️ DataChannel fermé côté edge")

        @self.channel.on("message")
        def on_message(message):
            print("📥 Message reçu côté edge:", message)
            data = json.loads(message)
            if data.get("type") == "command":
                self.engine.controls.apply_remote_command(data["data"])

    async def send_detections(self, detections):
        if self.channel and self.channel.readyState == "open":
            msg = {
                "type": "detections",
                "data": detections
            }
            self.channel.send(json.dumps(msg))