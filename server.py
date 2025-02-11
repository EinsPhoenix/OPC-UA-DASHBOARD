# server.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
import paho.mqtt.client as mqtt
import threading
import signal
import sys
import json
from typing import Dict, List, Optional
from datetime import datetime

class FanSpeedRequest(BaseModel):
    value: float = Field(..., ge=0, le=100, description="Fan speed value between 0 and 100")

class SensorData(BaseModel):
    temperature: List[float] = []
    humidity: List[float] = []
    fan_speed: List[float] = []
    timestamps: List[str] = []

class MQTTClientHandler:
    def __init__(self, broker_address: str = "https://test.mosquitto.org", broker_port: int = 1883):
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.client = mqtt.Client(protocol=mqtt.MQTTv311)  
        self.data = SensorData()
        self.max_history = 100
        self.connected = False
        self.setup_mqtt_client()

    def setup_mqtt_client(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        try:
            self.client.connect(self.broker_address, self.broker_port, keepalive=60)
            self.client.loop_start()
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}")
            sys.exit(1)

    def on_connect(self, client, userdata, flags, rc):
        connection_codes = {
            0: "Successfully connected",
            1: "Incorrect protocol version",
            2: "Invalid client identifier",
            3: "Server unavailable",
            4: "Bad username or password",
            5: "Not authorized"
        }
        print(f"MQTT Connection: {connection_codes.get(rc, 'Unknown error')}")
        
        if rc == 0:
            self.connected = True
            for topic in ["sensors/temperature", "sensors/humidity", "sensors/fan_speed"]:
                client.subscribe(topic)

    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        print(f"Disconnected from MQTT broker with code: {rc}")
        if rc != 0:
            print("Attempting to reconnect...")
            try:
                self.client.reconnect()
            except Exception as e:
                print(f"Reconnection failed: {e}")

    def on_message(self, client, userdata, msg):
        try:
            value = float(msg.payload.decode())
            timestamp = datetime.now().isoformat()
            
            topic_mapping = {
                "sensors/temperature": "temperature",
                "sensors/humidity": "humidity",
                "sensors/fan_speed": "fan_speed"
            }
            
            if msg.topic in topic_mapping:
                data_key = topic_mapping[msg.topic]
                data_list = getattr(self.data, data_key)
                data_list.append(value)
                self.data.timestamps.append(timestamp)
                
                # Keep only the last max_history values
                while len(data_list) > self.max_history:
                    data_list.pop(0)
                    self.data.timestamps.pop(0)
                    
        except Exception as e:
            print(f"Error processing message on topic '{msg.topic}': {e}")

    def set_fan_speed(self, value: float) -> None:
        if not 0 <= value <= 100:
            raise ValueError("Fan speed must be between 0 and 100")
        
        if not self.connected:
            raise Exception("MQTT client is not connected")
            
        try:
            result = self.client.publish("commands/set_fan_speed", str(value), qos=1)
            if not result.is_published():
                result.wait_for_publish()
            print(f"Fan speed command published: {value}")
        except Exception as e:
            raise Exception(f"Failed to set fan speed: {e}")

    def stop(self):
        print("Stopping MQTT client...")
        self.client.loop_stop()
        self.client.disconnect()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mqtt_handler = MQTTClientHandler()

@app.get("/data", response_model=SensorData)
async def get_data():
    return mqtt_handler.data

@app.post("/set_fan_speed")
async def set_fan_speed(request: FanSpeedRequest):
    try:
        mqtt_handler.set_fan_speed(request.value)
        return {"status": "success", "message": f"Fan speed set to {request.value}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def signal_handler(signum, frame):
    print("\nShutting down server...")
    mqtt_handler.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)