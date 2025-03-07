# OPC UA Dashboard

This project serves as an interface for monitoring and managing OPC UA servers via a user-friendly dashboard. Follow the steps below to set up and use the application effectively.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Setup Instructions](#setup-instructions)
3. [Configuring the OPC UA Server](#configuring-the-opc-ua-server)
4. [Running the Dashboard](#running-the-dashboard)
5. [How to use the Dashboard](#how-to-use-the-dashboard)

---

## Prerequisites

- **Python** (3.8 or higher recommended)
- **pip** (Python package manager)
- **Raspberry Pi** (optional, used as an OPC UA server)
- Installed and configured OPC UA server on Raspberry Pi or other devices

---

## Setup Instructions 
### 0. The testing Server
You have to do one thing and thats:
```bash
.\start.ps1
```
,now ignore the rest.
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

### 3. Install Requirements and make migrations
Install the dependencies listed in the `requirements.txt` file:
```bash
pip install -r requirements.txt
```


The migrations part:
```bash
    python manage.py makemigrations opcuaDash
    python manage.py migrate
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



## How to use the Dashboard
When something makes a sound you can click it.
S
1. The slider is at default at 48 when you want the automatic mode slide it down to 0
![alt text](image.png)

2. The top row is the opc-ua dashboard, its connected to the server and makes an api call to the backend
![alt text](image-1.png)

3. In the middle there are 3 diagrams which represent the live weather
![alt text](image-2.png)

4. At the bottom there are 3 diagrams which represent the energy price per hour based on the load, the current load and the energy price per MWH in euro. Here you can click the current load to get a detail-view
![alt text](image-3.png)

![alt text](image-4.png)

5. You noticed the popup at the beginning its a small reminder, who made this thing and its kind of funny

## TODO: 

- under Analytics add Raspberry vitals

- relative humidity und absolute value temperature

- pop up with our names and a short sentence 
