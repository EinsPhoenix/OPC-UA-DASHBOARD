from opcua import Client
import threading
import asyncio
import json
import signal
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import uvicorn
import time
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000", "http://127.0.0.1:5000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class OPCUAClient:
    def __init__(self, server_url):
        self.client = Client(server_url)
        self.client.connect()

        # Find ID containing node
        node = self.find_node_by_displayname("NodeIDs", path=["Objects", "Device"])
        node_ids_variable = self.client.get_node(node)
        node_ids_json = node_ids_variable.get_value()
        self.node_ids = json.loads(node_ids_json)
        print(self.node_ids)

        self.temperature_node = self.client.get_node(self.node_ids["Temperature"])
        self.humidity_node = self.client.get_node(self.node_ids["Humidity"])
        self.fan_speed_node = self.client.get_node(self.node_ids["FanSpeed"])
        self.set_fan_speed_node = self.client.get_node(self.node_ids["SetFanSpeed"])

        self.running = True
        self.data = {"temperature": [], "humidity": [], "fan_speed": []}

        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Handler für STRG+C"""
        print("\nProgramm wird beendet...")
        self.stop()
        sys.exit(0)

    def find_node_by_displayname(self, display_name, parent_node=None, path=None):
        if parent_node is None:
            parent_node = self.client.get_root_node()

        if path is not None:
            current_node = parent_node
            for node_name in path:
                found = False
                for child in current_node.get_children():
                    if child.get_display_name().Text == node_name:
                        current_node = child
                        found = True
                        break
                if not found:
                    return None

            for child in current_node.get_children():
                if child.get_display_name().Text == display_name:
                    return child
            return None

        def recursive_search(node):
            if node.get_display_name().Text == display_name:
                return node

            for child in node.get_children():
                result = recursive_search(child)
                if result is not None:
                    return result
            return None

        return recursive_search(parent_node)

    def fetch_data(self):
        """Fetch data from the server periodically and store it."""
        while self.running:
            try:
                self.data["temperature"].append(self.temperature_node.get_value())
                self.data["humidity"].append(self.humidity_node.get_value())
                self.data["fan_speed"].append(self.fan_speed_node.get_value())

                for key in self.data:
                    self.data[key] = self.data[key][-100:]
            except Exception as e:
                print(f"Error fetching data: {e}")
            time.sleep(1)

    def set_fan_speed(self, value):
        """Set the fan speed on the server."""
        try:
            self.set_fan_speed_node.set_value(float(value))
        except Exception as e:
            print(f"Error setting fan speed: {e}")

    def stop(self):
        """Stop fetching data and disconnect from the server."""
        print("Verbindung wird getrennt...")
        self.running = False
        self.client.disconnect()



opc_client = OPCUAClient("opc.tcp://localhost:4840/freeopcua/server/")


data_thread = threading.Thread(target=opc_client.fetch_data, daemon=True)
data_thread.start()




class FanSpeedRequest(BaseModel):
    value: float

@app.get("/data")
async def get_data():
    """Get the current sensor data."""
    
    return JSONResponse(opc_client.data)

@app.post("/set_fan_speed")
async def set_fan_speed(request: FanSpeedRequest):
    """Set the fan speed via the API."""
    try:
        opc_client.set_fan_speed(request.value)
        return {"status": "success", "message": f"Fan speed set to {request.value}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting fan speed: {e}")


def signal_handler(signum, frame):
    print("\nShutting down server...")
    opc_client.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    # Run FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=5000)
