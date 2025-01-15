# OPC UA Dashboard

This project serves as an interface for monitoring and managing OPC UA servers via a user-friendly dashboard. Follow the steps below to set up and use the application effectively.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Setup Instructions](#setup-instructions)
3. [Configuring the OPC UA Server](#configuring-the-opc-ua-server)
4. [Running the Dashboard](#running-the-dashboard)

---

## Prerequisites

- **Python** (3.8 or higher recommended)
- **pip** (Python package manager)
- **Raspberry Pi** (optional, used as an OPC UA server)
- Installed and configured OPC UA server on Raspberry Pi or other devices

---

## Setup Instructions

### 1. Remove Showcase Script
The `server.py` file provided in the repository is for showcase purposes only. **Delete this file** to avoid confusion, and add the following lines to your code:

```bash
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
```

### 2. Create a Virtual Environment
Run the following command to create a virtual environment:
```bash
python -m venv venv
```
Activate the virtual environment:
- **Windows**: `venv\Scripts\activate`
- **Linux/Mac**: `source venv/bin/activate`

### 3. Install Requirements
Install the dependencies listed in the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

---

## Configuring the OPC UA Server

### 1. Start the OPC UA Server
Start your OPC UA server on the Raspberry Pi (or any device you are using). Ensure the server is running and accessible.

### 2. Locate Node IDs
Retrieve the Node IDs from your OPC UA server. These will be used to configure the dashboard.

### 3. Update the Node IDs and Server Link in the upcuaclient.py
- Replace the placeholder Node IDs in the configuration file with the Node IDs from your server.
    ![Alt text](./Screenshot%202025-01-13%20075437.png)
- Update the server URL to point to your OPC UA server.
    ![Alt text](./Screenshot%202025-01-13%20075615.png)


---

## Running the Dashboard

After completing the configuration:
1. Start the Django development server:
   ```bash
   python manage.py runserver
   ```
2. Open your web browser and navigate to `http://127.0.0.1:8000/` to access the dashboard.



