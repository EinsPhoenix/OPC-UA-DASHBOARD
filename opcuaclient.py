import asyncio
from paho.mqtt import client as mqtt_client
from typing import Optional
import json
import time
import random
import board
import adafruit_dht
import RPi.GPIO as GPIO

class SensorClient:
    def __init__(self, broker: str = "192.168.50.58", port: int = 1883):
        # MQTT setup
        self.broker = broker
        self.port = port
        self.client_id = f"mqtt_sensor_client_{random.randint(0, 1000)}"
        self.set_fan_speed_value: Optional[float] = None
        self.connected = False
        
        # GPIO setup
        self.sensorPIN = 4
        self.luefterPIN = 13
        self.ledPIN = 23
        
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.luefterPIN, GPIO.OUT)
        GPIO.setup(self.ledPIN, GPIO.OUT)
        
        # Initialize DHT22 sensor
        self.dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False)
        
        # Start with everything off
        GPIO.output(self.luefterPIN, GPIO.LOW)
        GPIO.output(self.ledPIN, GPIO.LOW)
        
        # Connect to MQTT broker
        self.client = self.connect_mqtt()
        
        # Startup sequence - blink LED 3 times
        print("Starting up sensor client...")
        self.blink_led(3)
        
    def blink_led(self, times=1):
        """Blink the LED the specified number of times"""
        for _ in range(times):
            GPIO.output(self.ledPIN, GPIO.HIGH)
            time.sleep(0.5)
            GPIO.output(self.ledPIN, GPIO.LOW)
            time.sleep(0.5)
        
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
                   
                    self.set_fan_speed(self.set_fan_speed_value)
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
            client.username_pw_set("admin", "admin")
            client.connect(self.broker, self.port)
            
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
    
    def set_fan_speed(self, speed_percent):
        """Control the physical fan based on speed percentage"""
        if speed_percent > 0:
            GPIO.output(self.luefterPIN, GPIO.HIGH)
            GPIO.output(self.ledPIN, GPIO.HIGH)  
        else:
            GPIO.output(self.luefterPIN, GPIO.LOW)
            GPIO.output(self.ledPIN, GPIO.LOW)  

    async def read_sensor_data(self) -> tuple:
        """Read real sensor data from DHT22."""
        temperature = None
        humidity = None
        retry_count = 0
        max_retries = 3
        
        
        while (temperature is None or humidity is None) and retry_count < max_retries:
            try:
                temperature = self.dhtDevice.temperature
                humidity = self.dhtDevice.humidity
                print(f"Read from sensor: Temperature={temperature:.1f}°C, Humidity={humidity}%")
            except RuntimeError as error:
                print(f"DHT sensor read error: {error.args[0]}")
                retry_count += 1
                await asyncio.sleep(2.0)
            except Exception as error:
                print(f"Unexpected error: {str(error)}")
                break
        
     
        if temperature is None:
            temperature = random.uniform(20, 30)
            print(f"Using fallback temperature: {temperature:.1f}°C")
        
        if humidity is None:
            humidity = random.uniform(40, 60)
            print(f"Using fallback humidity: {humidity}%")
            
       
        if self.set_fan_speed_value is not None:
            fan_speed = self.set_fan_speed_value
        else:
            fan_speed = 0.0  
            
        return temperature, humidity, fan_speed

    async def publish_data(self):
        """Publish sensor data to MQTT broker."""
        if not self.connected:
            print("Not connected to MQTT broker. Attempting to reconnect...")
            self.reconnect()
            return

        temperature, humidity, fan_speed = await self.read_sensor_data()
        
       
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
        """Main loop for the sensor client."""
        try:
            print("Sensor client running. Press Ctrl+C to exit.")
            while True:
                await self.publish_data()
                await asyncio.sleep(5)  
        except asyncio.CancelledError:
            print("Shutting down sensor client...")
        finally:
            # Clean up
            self.client.loop_stop()
            self.client.disconnect()
            GPIO.output(self.luefterPIN, GPIO.LOW)
            GPIO.output(self.ledPIN, GPIO.LOW)
            GPIO.cleanup()
            print("GPIO cleaned up and MQTT client disconnected.")

async def main():
    try:
        sensor_client = SensorClient()
        await sensor_client.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    asyncio.run(main())
    
    
