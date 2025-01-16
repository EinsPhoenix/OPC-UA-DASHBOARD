from opcua import Server
import random
import asyncio
import json


async def run_server():
  
    server = Server()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")
    server.set_server_name("Example OPC UA Server")

    
    uri = "http://example.org"
    idx = server.register_namespace(uri)


    
    try:
        
        device = server.nodes.objects.add_object(idx, "Device")
        
        

      
        fan_speed = device.add_variable(idx, "FanSpeed", 0.0)
        temperature = device.add_variable(idx, "Temperature", 0.0)
        humidity = device.add_variable(idx, "Humidity", 0.0)
        set_fan_speed = device.add_variable(idx, "SetFanSpeed", 0.0)

       
        set_fan_speed.set_writable()

        
        node_ids = {
            "FanSpeed": fan_speed.nodeid.to_string(),
            "Temperature": temperature.nodeid.to_string(),
            "Humidity": humidity.nodeid.to_string(),
            "SetFanSpeed": set_fan_speed.nodeid.to_string(),
        }
        
        node_ids_variable = device.add_variable(
        idx, "NodeIDs", json.dumps(node_ids)
        )
        node_ids_variable.set_writable(False)
        
        print(f"NodeIDs variable created with NodeID: {node_ids}")


  
        server.start()
        print("Server started on opc.tcp://0.0.0.0:4840/freeopcua/server/")

        while True:
       
            current_set_fan_speed = set_fan_speed.get_value()

           
            if current_set_fan_speed != 0:
                fan_speed.set_value(current_set_fan_speed)
            else:
                fan_speed.set_value(random.uniform(0, 100))

            
            temperature.set_value(random.uniform(1, 50))
            humidity.set_value(random.uniform(10, 100))

       
            await asyncio.sleep(1)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        server.stop()
        print("Server stopped.")


if __name__ == "__main__":
    asyncio.run(run_server())
