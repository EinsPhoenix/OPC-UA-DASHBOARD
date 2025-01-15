from opcua import Server
import random
import asyncio
import json


async def run_server():
    # Create OPC UA Server
    server = Server()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")
    server.set_server_name("Example OPC UA Server")

    # Register namespace
    uri = "http://example.org"
    idx = server.register_namespace(uri)


    # Add objects and variables
    try:
        # Create device object
        device = server.nodes.objects.add_object(idx, "Device")
        
        

        # Add variables
        fan_speed = device.add_variable(idx, "FanSpeed", 0.0)
        temperature = device.add_variable(idx, "Temperature", 0.0)
        humidity = device.add_variable(idx, "Humidity", 0.0)
        set_fan_speed = device.add_variable(idx, "SetFanSpeed", 0.0)

        # Make set_fan_speed writable
        set_fan_speed.set_writable()

        # Create a JSON representation of NodeIds
        node_ids = {
            "FanSpeed": fan_speed.nodeid.to_string(),
            "Temperature": temperature.nodeid.to_string(),
            "Humidity": humidity.nodeid.to_string(),
            "SetFanSpeed": set_fan_speed.nodeid.to_string(),
        }
        # Add NodeIds JSON as a new variable
        node_ids_variable = device.add_variable(
        idx, "NodeIDs", json.dumps(node_ids)
        )
        node_ids_variable.set_writable(False)
        
        print(f"NodeIDs variable created with NodeID: {node_ids}")


        # Start the server
        server.start()
        print("Server started on opc.tcp://0.0.0.0:4840/freeopcua/server/")

        while True:
            # Get current set fan speed
            current_set_fan_speed = set_fan_speed.get_value()

            # Set fan speed based on set value or random
            if current_set_fan_speed != 0:
                fan_speed.set_value(current_set_fan_speed)
            else:
                fan_speed.set_value(random.uniform(0, 100))

            # Update temperature and humidity
            temperature.set_value(random.uniform(1, 50))
            humidity.set_value(random.uniform(10, 100))

            # Wait for 1 second
            await asyncio.sleep(1)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        server.stop()
        print("Server stopped.")


if __name__ == "__main__":
    asyncio.run(run_server())
