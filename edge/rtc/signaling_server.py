import asyncio
import json
import websockets

peers = {}
pending_messages = {"edge": [], "dashboard": []}

async def handler(websocket):
    role = None
    try:
        async for message in websocket:
            data = json.loads(message)

            if data["type"] == "register":
                role = data["role"]
                peers[role] = websocket
                print(f"{role} enregistré")

                if pending_messages[role]:
                    for pending in pending_messages[role]:
                        await websocket.send(pending)
                    pending_messages[role].clear()

                continue

            target = "dashboard" if role == "edge" else "edge"

            if target in peers:
                await peers[target].send(message)
            else:
                pending_messages[target].append(message)

    except websockets.ConnectionClosed:
        pass
    finally:
        if role and role in peers and peers[role] == websocket:
            del peers[role]

async def main():
    async with websockets.serve(handler, "127.0.0.1", 8765):
        print("Signaling server on ws://127.0.0.1:8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())