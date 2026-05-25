import asyncio
import json
import websockets

from aiortc import RTCSessionDescription, RTCIceCandidate
from edge.simulation.game_engine import GameEngine
from edge.ai.detection_pipeline import detect_from_simulation
from edge.rtc.rtc_bridge import EdgeRTCBridge

SIGNALING_URL = "ws://127.0.0.1:8765"


async def run():
    engine = GameEngine()
    rtc = EdgeRTCBridge(engine, None)

    async with websockets.connect(SIGNALING_URL) as ws:
        await ws.send(json.dumps({"type": "register", "role": "edge"}))

        @rtc.pc.on("icecandidate")
        async def on_icecandidate(candidate):
            if candidate:
                await ws.send(json.dumps({
                    "type": "ice-candidate",
                    "candidate": {
                        "candidate": candidate.candidate,
                        "sdpMid": candidate.sdpMid,
                        "sdpMLineIndex": candidate.sdpMLineIndex,
                    }
                }))

        offer = await rtc.pc.createOffer()
        await rtc.pc.setLocalDescription(offer)

        await ws.send(json.dumps({
            "type": "offer",
            "sdp": rtc.pc.localDescription.sdp,
            "sdpType": rtc.pc.localDescription.type
        }))

        async def signaling_listener():
            async for message in ws:
                data = json.loads(message)
                print("Message signaling reçu:", data["type"])

                if data["type"] == "answer":
                    await rtc.pc.setRemoteDescription(
                        RTCSessionDescription(sdp=data["sdp"], type=data["sdpType"])
                    )

                elif data["type"] == "ice-candidate":
                    c = data["candidate"]
                    try:
                        candidate = RTCIceCandidate(
                            component=1,
                            foundation="0",
                            ip="0.0.0.0",
                            port=9,
                            priority=0,
                            protocol="udp",
                            type="host",
                            sdpMid=c.get("sdpMid"),
                            sdpMLineIndex=c.get("sdpMLineIndex"),
                            tcpType=None,
                            relatedAddress=None,
                            relatedPort=None,
                        )
                        candidate.candidate = c.get("candidate")
                        await rtc.pc.addIceCandidate(candidate)
                    except Exception as e:
                        print("Erreur addIceCandidate:", e)

        listener_task = asyncio.create_task(signaling_listener())

        while engine.running:
            engine.update()
            engine.draw()

            detections = detect_from_simulation(engine.env, engine.robot)

            await rtc.send_detections(detections)
            await asyncio.sleep(1 / 30)

        listener_task.cancel()
        engine.stop()

if __name__ == "__main__":
    asyncio.run(run())