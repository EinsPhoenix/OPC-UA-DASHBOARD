from opcua import Client
import threading
import time

class OPCUAClient:
    def __init__(self, server_url):
        self.client = Client(server_url)
        self.client.connect()
        self.temperature_node = self.client.get_node("ns=2;i=3")
        self.humidity_node = self.client.get_node("ns=2;i=4")
        self.fan_speed_node = self.client.get_node("ns=2;i=2")
        self.set_fan_speed_node = self.client.get_node("ns=2;i=5")
        self.running = True
        self.data = {"temperature": [], "humidity": [], "fan_speed": []}

    def fetch_data(self):
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
        try:
            self.set_fan_speed_node.set_value(float(value))
        except Exception as e:
            print(f"Error setting fan speed: {e}")

    def stop(self):
        self.running = False
        self.client.disconnect()

opc_client = OPCUAClient("opc.tcp://localhost:4840/freeopcua/server/")


threading.Thread(target=opc_client.fetch_data, daemon=True).start()
