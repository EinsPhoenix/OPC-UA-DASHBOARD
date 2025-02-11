# client.py
import random
import asyncio
from paho.mqtt import client as mqtt_client
from typing import Optional
from datetime import datetime
import json
import time

class SensorSimulator:
    def __init__(self, broker: str = "https://test.mosquitto.org", port: int = 1883):
        self.broker = broker
        self.port = port
        self.client_id = f"mqtt_sensor_simulator_{random.randint(0, 1000)}"
        self.set_fan_speed_value: Optional[float] = None
        self.connected = False
        self.client = self.connect_mqtt()
        
    def connect_mqtt(self) -> mqtt_client.Client:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
                self.connected = True
                client.subscribe("commands/set_fan_speed", qos=1)
            else:
                print(f"Failed to connect, return code {rc}")
                self.connected = False

        def on_message(client, userdata, msg):
            if msg.topic == "commands/set_fan_speed":
                try:
                    self.set_fan_speed_value = float(msg.payload.decode())
                    print(f"New fan speed received: {self.set_fan_speed_value}")
                except Exception as e:
                    print(f"Error processing fan speed command: {e}")

        def on_disconnect(client, userdata, rc):
            self.connected = False
            print(f"Disconnected with result code: {rc}")
            if rc != 0:
                print("Unexpected disconnection. Attempting to reconnect...")
                self.reconnect()

        client = mqtt_client.Client(client_id=self.client_id, protocol=mqtt_client.MQTTv311)
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        
        try:
            client.connect(self.broker, self.port)
            # Wait for connection to be established
            client.loop_start()
            timeout = 10
            start_time = time.time()
            while not self.connected and time.time() - start_time < timeout:
                time.sleep(0.1)
            if not self.connected:
                raise Exception("Failed to connect within timeout period")
        except Exception as e:
            print(f"Failed to connect to broker: {e}")
            raise
            
        return client

    def reconnect(self):
        try:
            self.client.reconnect()
        except Exception as e:
            print(f"Reconnection failed: {e}")

    async def generate_sensor_data(self) -> tuple:
        """Generate simulated sensor data."""
        temperature = random.uniform(20, 30)
        humidity = random.uniform(40, 60)
        
        if self.set_fan_speed_value is not None:
            fan_speed = self.set_fan_speed_value
        else:
            fan_speed = random.uniform(0, 100)
            
        return temperature, humidity, fan_speed

    async def publish_data(self):
        """Publish sensor data to MQTT broker."""
        if not self.connected:
            print("Not connected to MQTT broker. Attempting to reconnect...")
            self.reconnect()
            return

        temperature, humidity, fan_speed = await self.generate_sensor_data()
        
        # Create a data packet for each sensor
        for topic, value in [
            ("sensors/temperature", temperature),
            ("sensors/humidity", humidity),
            ("sensors/fan_speed", fan_speed)
        ]:
            try:
                result = self.client.publish(topic, str(value), qos=1)
                result.wait_for_publish()
            except Exception as e:
                print(f"Error publishing to {topic}: {e}")
                
        print(f"Published: Temperature={temperature:.2f}°C, "
              f"Humidity={humidity:.2f}%, Fan Speed={fan_speed:.2f}%")

    async def run(self):
        """Main loop for the sensor simulator."""
        try:
            while True:
                await self.publish_data()
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            print("Shutting down sensor simulator...")
        finally:
            self.client.loop_stop()
            self.client.disconnect()

async def main():
    simulator = SensorSimulator()
    try:
        await simulator.run()
    except KeyboardInterrupt:
        print("\nShutting down...")

if __name__ == "__main__":
    asyncio.run(main())
