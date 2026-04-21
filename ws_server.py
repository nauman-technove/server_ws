import asyncio
import websockets
import json


async def handler(websocket):
    print("Client connected")

    try:
        async for message in websocket:
            data = json.loads(message)
            print("\n📩 Received Event:")
            print(f"Device: {data.get('device_id')}")
            print(f"Frame: {data.get('frame_index')}")
            print(f"Latency: {data.get('inference_latency_ms')} ms")
            print(f"Vector length: {len(data.get('clip_vector', []))}")

    except Exception as e:
        print("Error:", str(e))

    finally:
        print("Client disconnected")


async def main():
    server = await websockets.serve(handler, "localhost", 3001)
    print("🚀 WebSocket server running on ws://localhost:3001")
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())