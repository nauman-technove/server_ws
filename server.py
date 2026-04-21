import asyncio
import json
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import websockets

app = FastAPI()

# Store live data
connected_clients = 0
latest_events = []

# ---------------- WebSocket SERVER ----------------
async def ws_handler(websocket):
    global connected_clients
    connected_clients += 1
    print("Client connected")

    try:
        async for message in websocket:
            data = json.loads(message)

            event = {
                "device": data.get("device_id"),
                "frame": data.get("frame_index"),
                "latency": data.get("inference_latency_ms"),
                "vector_length": len(data.get("clip_vector", [])),
            }

            latest_events.append(event)

            # keep only last 20 events
            if len(latest_events) > 20:
                latest_events.pop(0)

    except Exception as e:
        print("Error:", str(e))

    finally:
        connected_clients -= 1
        print("Client disconnected")


# ---------------- Start WS server ----------------
async def start_ws():
    return await websockets.serve(ws_handler, "0.0.0.0", 3001)


# ---------------- HTTP Routes ----------------
@app.get("/")
def home():
    return HTMLResponse("""
    <html>
        <head>
            <title>WebSocket Monitor</title>
            <style>
                body { font-family: Arial; padding: 20px; }
                .card {
                    border: 1px solid #ddd;
                    padding: 10px;
                    margin-bottom: 10px;
                    border-radius: 8px;
                }
                .header { font-size: 20px; margin-bottom: 10px; }
            </style>
        </head>
        <body>
            <div class="header">🚀 WebSocket Monitor</div>
            <div><strong>Connected Clients:</strong> <span id="clients">0</span></div>
            
            <h3>📩 Events</h3>
            <div id="events"></div>

            <script>
                async function fetchData() {
                    const res = await fetch('/status');
                    const data = await res.json();

                    // Update client count
                    document.getElementById('clients').innerText = data.clients;

                    // Render events
                    const container = document.getElementById('events');
                    container.innerHTML = "";

                    data.events.reverse().forEach(event => {
                        const div = document.createElement('div');
                        div.className = "card";

                        div.innerHTML = `
                            <strong>Device:</strong> ${event.device}<br/>
                            <strong>Frame:</strong> ${event.frame}<br/>
                            <strong>Latency:</strong> ${event.latency} ms<br/>
                            <strong>Vector Length:</strong> ${event.vector_length}
                        `;

                        container.appendChild(div);
                    });
                }

                setInterval(fetchData, 1000);
                fetchData();
            </script>
        </body>
    </html>
    """)

@app.get("/status")
def status():
    return {
        "clients": connected_clients,
        "events": latest_events
    }


# ---------------- Main ----------------

@app.on_event("startup")
async def startup():
    await start_ws()