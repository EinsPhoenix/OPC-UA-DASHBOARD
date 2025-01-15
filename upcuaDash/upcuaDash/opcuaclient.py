from opcua import Client
import threading
import time
import json
import signal
import sys

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
                
                # print(self.data)

               
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
 # Thread als Daemon starten
data_thread = threading.Thread(target=opc_client.fetch_data, daemon=True)
data_thread.start()
if __name__ == "__main__":
    try:
       
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
       
        opc_client.stop()
        
