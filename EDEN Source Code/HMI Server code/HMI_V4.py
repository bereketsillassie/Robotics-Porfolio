from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import threading
import paho.mqtt.client as mqtt
import webbrowser
import json
import serial
from datetime import datetime, timedelta
import schedule 
from queue import Queue
import time 


# FLASK SETUP --------------------------------------------------------------------------

app = Flask(__name__)

# Is used so site auto opens
def open_browser():
    webbrowser.open("http://127.0.0.1:5000")  # Change this URL if needed


# APP SETUP --------------------------------------------------------------------------
API_KEY = "mysecretkey123"

event_log = []


# MQTT SETUP -------------------------------------------------------------------------
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
MQTT_PLANTPOD = ("plantPod1/data","plantPod2/data","plantPod3/data","plantPod4/data")
MQTT_PUMP_CMD = "pump/ctl"
MQTT_SOL_CMD = "sol/ctl"
MQTT_LIGHT_CMD = "light/ctl"
MQTT_MODE_CMD = "mode/ctl"
MQTT_GANTRY_CMD = "gantry/ctl"
MQTT_TANK = "tank/data"

#Manual
# Gantry move left right and choose top or bottom
# irigation pump on choose top or bottom
# Lights on or off top or bottom (Slider?)

#Auto
# Control the lights
#   - Adjust for ambient light
#   - 12 hour cycle
# Control the water
#   - not wet make wet

#App integration
# Send logs
#   - Water refil nonification
#   - Send Sensor info




# NPK set up
ser = serial.Serial()
npk_query = bytearray([0x01, 0x03, 0x00, 0x1E, 0x00, 0x03, 0x65, 0xCD])

watering_queue = Queue()
currently_watering = False

# -------------------------- DATA BLOCKS--------------------------------------
# Sensor Data 
sensor_data = {
    "light": 1,
    "temperature": 1,
    "humidity": 1,
    "moisture": 1,

    "light2": 1,
    "temperature2": 1,
    "humidity2": 1,
    "moisture2": 1,

    "light3": 1,
    "temperature3": 1,
    "humidity3": 1,
    "moisture3": 1,

    "light4": 1,
    "temperature4": 1,
    "humidity4": 1,
    "moisture4": 1,

}




# Digital Emergency stop state --
#   - E-Stop Data sent as: "status" ; Ex: "0"
emergency_stop = {"status": False}

# Pump state --
#   Pump Data sent as: "status" ; Ex: "0"
pump_ctl = {"status": False}

# Solenoid state --
#   Solenoid Data sent as: "top bottom" ; Ex: "0 0"
sol_ctl = {
    "top": {"status": False},
    "bottom": {"status": False}
}

# Gantry state --
#   Gantry Data sent as: "top bottom" ; Ex: "0 0"
#   False = Left  |  True = Right
gantry_ctl = {
    "top": {"status": False},
    "bottom": {"status": False}
}

# Light Intensity --
#   Light Data sent as: "topR topL bottomR bottomL" ; Ex: "0 0 0 0"
light_ctl = {
    "topR": {"intensity": 0},
    "topL": {"intensity": 0},
    "bottomR": {"intensity": 0},
    "bottomL": {"intensity": 0}
}

# Control Mode --
#   Mode Data sent as: "status" ; Ex: "Auto"
#   False = MANUAL  |  True = AUTO
mode_ctl = {"status": False}

# NPK Data
npk_results = {
    "n": 5,
    "p": 6,
    "k": 7
}

# tank state --
#   Tank Data sent as: "status" ; Ex: "False"
tank_state = {"status": False}
last_low_alert = None
last_low_water_event = None  # Keep track of last event time

plant_config = {
    "plantPod1": {
        "moisture_threshold": 35,
        "buffer": 0.1,
        "watering_duration_sec": 5,
        "light_threshold": 100,
        "light_schedule": {
            "on_hour": 8,
            "off_hour": 20,
            "check_interval_min": 5
        }
    },

    "plantPod2": {
        "moisture_threshold": 35,
        "buffer": 0.1,
        "watering_duration_sec": 5,
        "light_threshold": 100,
        "light_schedule": {
            "on_hour": 8,
            "off_hour": 20,
            "check_interval_min": 5
        }
    },

    "plantPod3": {
        "moisture_threshold": 35,
        "buffer": 0.1,
        "watering_duration_sec": 5,
        "light_threshold": 100,
        "light_schedule": {
            "on_hour": 8,
            "off_hour": 20,
            "check_interval_min": 5
        }
    },

    "plantPod4": {
        "moisture_threshold": 35,
        "buffer": 0.1,
        "watering_duration_sec": 5,
        "light_threshold": 100,
        "light_schedule": {
            "on_hour": 8,
            "off_hour": 20,
            "check_interval_min": 5
        }
    }
}


# -----------------------------------------------------------------


# HTML content stored in a string message for the app to use 
# (not much comments for the body)
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>EDEN HMI-SYSTEM</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
   
    <style>
        :root {
            --primary-color: #ecf0f1; /* Light background for text elements */
            --secondary-color: #34495e; /* Earthy dark green for panels */
            --accent-color: #27ae60; /* Bright green for buttons and accents */
            --danger-color: #c0392b; /* Red for emergency or warning buttons */
            --button-color: rgb(78,192,43); /* Red for emergency or warning buttons */
            --success-color: #2ecc71; /* Light green for success states */
            --text-color: #2e5339; /* !Text color for readability */
            --bg-color: #5A5B5D; /* !Overall background color */
            --button-padding: 20px 30px; /* Padding for buttons */
            --font-size: 16px; /* Base font size */
            --control-gap: 10px; /* Gap between control elements */
        }

        /* Just Moves it up and changes border */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }


        body {
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color); /* Earthy green background */
            color: var(--text-color);
            overflow: hidden;
            display: flex;
            height: 100vh;
        }

        /* LEFT-SIDE FIXED MENU */
        .left-half {
            width: 20%; /* Left half takes 1/5 of the screen */
            height: 100vh; /* Full height */
            position: fixed; /* Keeps it in place */
            background: linear-gradient(to top, #234935, #151936);
            flex-direction: column;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            box-sizing: border-box;
        }

        .left-half a {
            display: block;
            color: white;
            padding: 15px;
            text-decoration: none;
            font-size: 18px;
            text-align: center;
            width: 100%;
        }

        .left-half a:hover {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
        }

        /* RIGHT SIDE CONTAINER */
        .right-half {
            width: 80%;
            height: 100vh; /* Ensure it fills the full viewport height */
            margin-left: 20%;
            background: linear-gradient(to top, #2A2A2A, #464646);
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 20px;
            overflow: auto;
            box-sizing: border-box;
        }

        


        .header {
            width: 100%;
            background-color: var(--secondary-color);
            color: var(--primary-color);
            border-radius: 15px;
           
            padding: 20px 20px;
            font-size: 20px;
            font-weight: bold;
            text-align: center;
            align-items: center;
            margin-bottom: 15px;
            grid-column: span 1;
        }

        .pump {
            display: flex; /* Enables horizontal alignment */
            justify-content: space-around; /* Spreads the items evenly */
            align-items: center; /* Aligns them vertically */
            padding: 10px;
            gap: 15px; /* Adds spacing between items */  
            margin-bottom: 15px;
        }

        

       


        .title {
            font-size: 20px;
            font-weight: 600;
            color: var(--accent-color);
        }

        .logo {
            font-size: 60px;
            font-weight: bold;
            margin-top: 20px;
            color: var(--accent-color);
            text-align: center;
        }

        .text1 {
            font-size: 24px;
            font-weight: bold;
            margin-top: 20px;
            color: var(--accent-color);
            text-align: center;
        }

        .time-date {
            font-size: 30px;
            color: var(--primary-color);
        }

        #date-time {
            text-align: center;  /* Center align the content */
            font-size: 30px;
            color: #ffffff; /* Adjust text color */
        }


        #date-time div {
            margin: 5px 0; /* Add space between date and time */
        }

        .status {
            padding: 4px 8px;
            border-radius: 15px;
            background: var(--success-color);
            color: white;
            font-size: 12px;
        }

        .plant-grid {
            display: grid;
            
            grid-template-columns: repeat(2, 1fr); /* 2 columns */
            gap: 20px;
            width: 100%;
            height: 100%
        }

        .plant-pod {
            background-color: var(--secondary-color);
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }

        .plant-pod h3 {
            color: var(--accent-color); /* color of the title */
            font-size: 20px;
            text-align: center;
        }

        .plant-pod p {
            font-size: 25px;
            color: var(--primary-color); /* sensor infor*/
            text-align: center;
            margin: 10px 0;
        }

        .plant-pod .sensor-data {
            font-weight: bold;
        }

        .button-group {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }

        button {
            background-color: var(--button-color);
            color: white;
            border: none;
            padding: var(--button-padding);
            border: none;
            border-radius: 4px;
            font-size: var(--font-size);
            transition: transform 0.1s, background 0.3s;
            cursor: pointer;
            margin-top: 10px;
        }

        button:hover {
            background-color: #25a55a;
            transform: translateY(-1px);
        }


        .e-stop {
            background-color: var(--danger-color);
        }
        
        .e-stop:hover {
            background-color: #6B0001;
        }


        input[type="number"], input[type="text"] {
            width: 60px;
            padding: 6px;
            border: 1px solid #555;
            border-radius: 4px;
            margin: 0 5px;
            background-color: var(--secondary-color);
            color: var(--text-color);
            font-size: var(--font-size);
            
        }

        input[type="number"]::placeholder, input[type="text"]::placeholder {
            color: var(--text-color);
        }

        .emergency-control {
            color: var(--primary-color);
            text-align: center;
        }

        .pump-control {
            color: var(--primary-color);
            text-align: center;
        }

        .npk-request {
            color: var(--primary-color);
            text-align: center;
        }
        
        
        .gantry-control {
            color: var(--primary-color);
            text-align: center;    
        }

        .sol-control {
            color: var(--primary-color);
            text-align: center;    
        }

        .mode-control {
            color: var(--primary-color);
            text-align: center;    
        }

        /* Manual control stuff ---------------------------*/
        .slider-container {
            
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-top: 20px;
            color: var(--primary-color);
        }

        .slider {
        
            width: 80%;
        }



        .container {
            display: grid;
            grid-template-columns: auto 1fr; /* Title on the left, content on the right */
            gap: 20px; /* Spacing between columns */
            width: 100%;
            height: 35%;
            background-color: var(--secondary-color);
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(158, 89, 89, 0.1);
            margin-bottom: 10px;
            justify-content: center;
        }

        .manualtitle {
            font-size: 20px;
            font-weight: bold;
            color: var(--primary-color);
            width: 25vh;
            grid-column: 1; /* Ensures title stays in the left column */
            display: flex;
            align-items: center; /* Centers text vertically */
            justify-content: center; /* Centers text horizontally (optional) */
            text-align: center; /* Ensures text is centered */
            /* height: 100%; Ensures it takes full height of its parent */
        }


        .manualcontent {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); /* Responsive button grid */
            gap: 10px; /* Space between buttons */
            width: 100%; /* Ensure it fills the available space */
            align-items: center;
            justify-content: center;
            
        }

        #manual-overlay {
            position: absolute;
            top: 0;
            left: 20%; /* Matches your manual page's left offset */
            width: 80%;
            height: 100vh;
            background-color: rgba(0, 0, 0, 0.4);
            z-index: 9999;
            display: none;  /* Start hidden */
            pointer-events: all;
        }


    
        

      

        /* PAGE SWITCHING --------------------------------*/
        .page {
            display: none;
        }

        .page.active {
            display: block;
        }
    </style>
    <script>
        function fetchSensorData() {
            fetch('/sensor-data')
                .then(response => response.json())
                .then(data => {
                    document.getElementById("light").innerText = data.light + " lux";
                    document.getElementById("temperature").innerText = data.temperature + " °C";
                    document.getElementById("humidity").innerText = data.humidity + "%";
                    document.getElementById("moisture").innerText = data.moisture + "%";
                    document.getElementById("light2").innerText = data.light2 + " lux";
                    document.getElementById("temperature2").innerText = data.temperature2 + " °C";
                    document.getElementById("humidity2").innerText = data.humidity2 + "%";
                    document.getElementById("moisture2").innerText = data.moisture2 + "%";
                    document.getElementById("light3").innerText = data.light3 + " lux";
                    document.getElementById("temperature3").innerText = data.temperature3 + " °C";
                    document.getElementById("humidity3").innerText = data.humidity3 + "%";
                    document.getElementById("moisture3").innerText = data.moisture3 + "%";
                    document.getElementById("light4").innerText = data.light4 + " lux";
                    document.getElementById("temperature4").innerText = data.temperature4 + " °C";
                    document.getElementById("humidity4").innerText = data.humidity4 + "%";
                    document.getElementById("moisture4").innerText = data.moisture4 + "%";
                });
        }

        let isEmergencyStopOn = false;
        function triggerEmergencyStop() {
            // Toggle the emergency stop status
            isEmergencyStopOn = !isEmergencyStopOn;

            // Send the new status (ON or OFF)
            fetch('/emergency-stop', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: isEmergencyStopOn })
            })
                .then(response => response.json())
                .then(data => {
                    alert(data.message); // Show the message returned from the server
                    document.getElementById("emergency-status").innerText = isEmergencyStopOn ? "ON" : "OFF"; // Update the status display

                    const overlay = document.getElementById("manual-overlay");
                    if (isEmergencyStopOn) {
                        overlay.style.display = "block";  // ESTOP BLOCK — lock controls
                    } else {
                        overlay.style.display = "none";   // NO ESTOP NO BLOCK — unlock controls
                    }

                    // If E-STOP is ON and system is in AUTO, revert to MANUAL
                    if (isEmergencyStopOn && modeselect) {
                        modeselect = false;  // Change internal flag
                        document.getElementById("mode-status").innerText = "MANUAL";

                        // Hide the overlay to re-enable manual control
                        // document.getElementById("manual-overlay").style.display = "none";

                        // Optionally notify backend
                        fetch('/mode-ctl', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ status: modeselect })  // false = manual
                        })
                        .then(response => response.json())
                        .then(data => console.log("Mode reverted to MANUAL due to E-STOP."));
                    }
                });
        }

        let isPumpOn = false;
        function triggerPump() {
            // Toggle the pump status
            isPumpOn = !isPumpOn;

            // Send the new status (ON or OFF)
            fetch('/pump-ctl', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: isPumpOn })
            })
                .then(response => response.json())
                .then(data => {
                    alert(data.message); // Show the message returned from the server
                    document.getElementById("pump-status").innerText = isPumpOn ? "ON" : "OFF"; // Update the status display
                });
        }
        
        let gantryStatus = {
            top: false,    // false represents OFF, true represents ON
            bottom: false
        };
        function triggerGantry(position) {
            // Toggle the Gantry status
            gantryStatus[position] = !gantryStatus[position];

            // Send the new status (ON or OFF)
            fetch('/gantry-ctl', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    position: position,  // Send the position (top or bottom)
                    status: gantryStatus[position]     // Send the new status
                })
            })
                .then(response => response.json())
                .then(data => {
                    alert(data.message); // Show the message returned from the server
                    
                    // Update the status display based on the position passed
                    const statusElement = document.getElementById(`${position}-gantry-status`);
                    if (statusElement) {
                        statusElement.innerText = gantryStatus[position] ? "Right" : "Left"; // Update the status display
                    }
                });
        }

        let solStatus = {
            top: false,    // false represents OFF, true represents ON
            bottom: false
        };
        function triggersol(position) {
            // Toggle the Solenoid status
            solStatus[position] = !solStatus[position];

            // Send the new status (ON or OFF)
            fetch('/sol-ctl', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    position: position,  // Send the position (top or bottom)
                    status: solStatus[position]     // Send the new status
                })
            })
                .then(response => response.json())
                .then(data => {
                    alert(data.message); // Show the message returned from the server
                    
                    // Update the status display based on the position passed
                    const statusElement = document.getElementById(`${position}-sol-status`);
                    if (statusElement) {
                        statusElement.innerText = solStatus[position] ? "OPEN" : "CLOSED"; // Update the status display
                    }
                });
        }

        let modeselect = false;
        function triggermode() {
            // Toggle the mode status
            if (isEmergencyStopOn) {
                alert("Cannot enter AUTO mode while Emergency Stop is engaged.");
                return; 
            }
            modeselect = !modeselect;

            // Send the new status (ON or OFF)
            fetch('/mode-ctl', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: modeselect })
            })
                .then(response => response.json())
                .then(data => {
                    alert(data.message); // Show the message returned from the server
                    document.getElementById("mode-status").innerText = modeselect ? "AUTO" : "MANUAL"; // Update the status display

                    // Show or hide the overlay based on mode
                    const overlay = document.getElementById("manual-overlay");
                    if (modeselect) {
                        overlay.style.display = "block";  // AUTO mode — lock controls
                    } else {
                        overlay.style.display = "none";   // MANUAL mode — unlock controls
                    }
                });
        }

        let LeftorRight = false;
        function triggerdirec() {
            // Toggle the pump status
            LeftorRight = !LeftorRight;

            // Send the new status (ON or OFF)
            fetch('/direction-ctl', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: LeftorRight })
            })
                .then(response => response.json())
                .then(data => {
                    alert(data.message); // Show the message returned from the server
                    document.getElementById("direction-status").innerText = LeftorRight ? "Left" : "Right"; // Update the status display
                });
        }

        function fetchNPKData() {
            fetch('/npk-results', {
                method: 'POST',
            })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    document.getElementById("n").innerText = data.n + " mm/kg";
                    document.getElementById("p").innerText = data.p + " mm/kg";
                    document.getElementById("k").innerText = data.k + " mm/kg";
                })
                .catch(error => console.error("Error fetching NPK data:", error));;
        }

        
        function sendSliderValue(position, value) {
            fetch('/light-ctl', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    position: position,  // Position (topR, topL, bottomR, bottomL)
                    intensity: value     // Intensity value from 0 to 100
                })
            })
            .then(response => response.json())
            .then(data => console.log(data.message));  // Log server response or handle it accordingly
        }

        function displayDateTime() {
            var date = new Date(); // Create a new Date object
            var dateString = date.toLocaleDateString(); // Format the date
            var timeString = date.toLocaleTimeString(); // Format the time
            document.getElementById("date").innerHTML = dateString; // Display date
            document.getElementById("time").innerHTML = timeString; // Display time
        }

        setInterval(displayDateTime, 1000); // Refresh every 1 second
       
        setInterval(fetchSensorData, 2000); // Refresh every 2 seconds
    </script>
</head>
<body>

    <!-- LEFT-SIDE FIXED MENU -->
    <div class="left-half">
        <div class="logo">EDEN </div>
        <div class="title">
            <div class="time-date">
                <div id="date"></div> <!-- Date will be displayed here -->
                <div id="time"></div> <!-- Time will be displayed here -->
            </div>
        </div>
        <div class="text1">HMI CONTROL SYSTEM</div>
        <a href="#" onclick="showPage('sensor')">PLANT INFO</a>
        <a href="#" onclick="showPage('manual_mode')">MANUAL CONTROL</a>
        <div class="mode-control">
            <p><strong>Mode Status:</strong> <span id="mode-status">MANUAL</span></p>
            <button onclick="triggermode('bottom')">MODE TOGGLE </button>
        </div>
        <div class="emergency-control">
            <p><strong>Emergency Stop Status:</strong> <span id="emergency-status">OFF</span></p>
            <button class="e-stop" onclick="triggerEmergencyStop()">EMERGENCY STOP</button>
        </div>
    </div>

    <!-- RIGHT-SIDE CHANGING CONTENT -->
    <div class="right-half">
        
        <div id="sensor" class="page active">
            <div class="header">
                <h2>SENSOR INFORMATION</h2>
            </div>
            <div class="plant-grid">
                <div class="plant-pod">
                    <h3>Plant Pod 1</h3>
                    <p><strong>Light Intensity:</strong> <span id="light">Loading...</span></p>
                    <p><strong>Temperature:</strong> <span id="temperature">Loading...</span></p>
                    <p><strong>Humidity:</strong> <span id="humidity">Loading...</span></p>
                    <p><strong>Soil Moisture:</strong> <span id="moisture">Loading...</span></p>
                </div>

                <div class="plant-pod">
                    <h3>Plant Pod 2</h3>
                    <p><strong>Light Intensity:</strong> <span id="light2">Loading...</span></p>
                    <p><strong>Temperature:</strong> <span id="temperature2">Loading...</span></p>
                    <p><strong>Humidity:</strong> <span id="humidity2">Loading...</span></p>
                    <p><strong>Soil Moisture:</strong> <span id="moisture2">Loading...</span></p>
                </div>

                <div class="plant-pod">
                    <h3>Plant Pod 3</h3>
                    <p><strong>Light Intensity:</strong> <span id="light3">Loading...</span></p>
                    <p><strong>Temperature:</strong> <span id="temperature3">Loading...</span></p>
                    <p><strong>Humidity:</strong> <span id="humidity3">Loading...</span></p>
                    <p><strong>Soil Moisture:</strong> <span id="moisture3">Loading...</span></p>
                </div>

                <div class="plant-pod">
                    <h3>Plant Pod 4</h3>
                    <p><strong>Light Intensity:</strong> <span id="light4">Loading...</span></p>
                    <p><strong>Temperature:</strong> <span id="temperature4">Loading...</span></p>
                    <p><strong>Humidity:</strong> <span id="humidity4">Loading...</span></p>
                    <p><strong>Soil Moisture:</strong> <span id="moisture4">Loading...</span></p>
                </div>
            </div>
        </div>

        <div id="manual_mode" class="page">
            <div class="header">
                <h2>MANUAL CONTROL</h2> 
            </div>
            <div class="header pump">
                <div class="pump-control">
                    <p><strong>Pump Status:</strong> <span id="pump-status">OFF</span></p>
                    <button onclick="triggerPump()">PUMP TOGGLE</button>
                </div>
                <div class="npk-request">
                    <p><strong>NPK Request:</strong> </p>
                    <button onclick="fetchNPKData()">GET DATA</button>
                </div>
            </div>
            <div class="container">
                <div class="manualtitle">TOP</div>
                <div class="manualcontent">
                    <div class="sol-control">
                        <p><strong>Sprayead Status:</strong> <span id="top-sol-status">CLOSED</span></p>
                        <button onclick="triggersol('top')">SPRAYHEAD TOGGLE (TOP)</button>
                    </div>
                    
                    <div class="gantry-control">
                        <p><strong>Gantry Status:</strong> <span id="top-gantry-status">---</span></p>
                        <button onclick="triggerGantry('top')">GANTRY TOGGLE (TOP)</button>
                    </div>
                    <div class="slider-container">
                        <label for="topL-slider">Top Left Lights:</label>
                        <input type="range" id="topL-slider" class="slider" min="0" max="100" value="0">
                        <p>Value: <span id="topL-slider-value">0</span></p>
                    </div>
                    <div class="slider-container">
                        <label for="topR-slider">Top Right Lights:</label>
                        <input type="range" id="topR-slider" class="slider" min="0" max="100" value="0">
                        <p>Value: <span id="topR-slider-value">0</span></p>
                    </div>
                    
                </div>   
            </div>
            <div class="container">
                <div class="manualtitle">BOTTOM</div>
                <div class="manualcontent">
                    <div class="sol-control">
                        <p><strong>Sprayead Status:</strong> <span id="bottom-sol-status">CLOSED</span></p>
                        <button onclick="triggersol('bottom')">SPRAYHEAD TOGGLE (BOTTOM)</button>
                    </div>
                    
                    <div class="gantry-control">
                        <p><strong>Gantry Status:</strong> <span id="bottom-gantry-status">---</span></p>
                        <button onclick="triggerGantry('bottom')">GANTRY TOGGLE (BOTTOM)</button>
                    </div>
                    <div class="slider-container">
                        <label for="bottomR-slider">Bottom Right Lights:</label>
                        <input type="range" id="bottomR-slider" class="slider" min="0" max="100" value="0">
                        <p>Value: <span id="bottomR-slider-value">0</span></p>
                    </div>
                    <div class="slider-container">
                        <label for="bottomL-slider">Bottom Left Lights:</label>
                        <input type="range" id="bottomL-slider" class="slider" min="0" max="100" value="0">
                        <p>Value: <span id="bottomL-slider-value">0</span></p>
                    </div>
                </div>
            </div>
            <div id="manual-overlay"></div>
        </div>
    </div>

    <!-- JAVASCRIPT TO SWITCH PAGES -->
    <script>
        function showPage(pageId) {
            document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
            document.getElementById(pageId).classList.add('active');
        }

        // Adding event listeners to sliders to update values dynamically
        document.getElementById("topR-slider").addEventListener("input", function() {
            const value = this.value;
            document.getElementById("topR-slider-value").textContent = value;  // Update display
            sendSliderValue('topR', value);  // Send the value to the server
        });

        document.getElementById("topL-slider").addEventListener("input", function() {
            const value = this.value;
            document.getElementById("topL-slider-value").textContent = value;  // Update display
            sendSliderValue('topL', value);  // Send the value to the server
        });

        document.getElementById("bottomR-slider").addEventListener("input", function() {
            const value = this.value;
            document.getElementById("bottomR-slider-value").textContent = value;  // Update display
            sendSliderValue('bottomR', value);  // Send the value to the server
        });

        document.getElementById("bottomL-slider").addEventListener("input", function() {
            const value = this.value;
            document.getElementById("bottomL-slider-value").textContent = value;  // Update display
            sendSliderValue('bottomL', value);  // Send the value to the server
        });
    </script>

</body>
</html>

"""


# -----------------------------------------------------------------

# Directs Flask to the html script
@app.route("/")
def index():
    return render_template_string(html_content)

#   _____ BUTTTON DIRECTIONS _____
@app.route("/sensor-data", methods=["GET"])
def get_sensor_data():
    return jsonify(sensor_data)

@app.route("/emergency-stop", methods=["POST"])
def handle_emergency_stop():
    global emergency_stop
    emergency_stop["status"] = request.json.get("status", False)
    pump_string = "0"
    ganrty_string = "0 0"

    
    client.publish(MQTT_PUMP_CMD, "False")
    client.publish(MQTT_GANTRY_CMD, "STOP STOP")
    client.publish(MQTT_SOL_CMD, "False False")
    client.publish(MQTT_LIGHT_CMD, "0 0 0 0")
    print("E-STOP: Published STOP command")
    
    return jsonify({"message": "E-STOP TOGGLED!", "status": emergency_stop["status"]})

@app.route("/pump-ctl", methods=["POST"])
def handle_pump():
    global pump_ctl
    status = request.json.get("status", False)
    

    if emergency_stop["status"] == False:
        pump_ctl["status"] = status
        pump_cmd = f"{pump_ctl['status']}"
        client.publish(MQTT_PUMP_CMD, pump_cmd)
        print(pump_cmd)
    return jsonify({"message": "PUMP TOGGLED!", "status": pump_ctl["status"]})

@app.route("/light-ctl", methods=["POST"])
def handle_light():
    global light_ctl
    position = request.json.get("position")
    intensity = request.json.get("intensity", 0)  # Getting intensity value from 0 to 100
    

    # Check if position exists in the light_ctl dictionary
    if position in light_ctl:
        if emergency_stop["status"] == False:
            light_ctl[position]["intensity"] = intensity
            light_cmd = f"{light_ctl['topR']['intensity']} {light_ctl['topL']['intensity']} {light_ctl['bottomR']['intensity']} {light_ctl['bottomL']['intensity']}"
            client.publish(MQTT_LIGHT_CMD, light_cmd)        
        return jsonify({"message": f"Light {position.upper()} intensity updated.", "intensity": light_ctl[position]["intensity"]})
    else:
        return jsonify({"message": "Invalid light position!"}), 400
  
@app.route("/sol-ctl", methods=["POST"])
def handle_sol():
    global sol_ctl
    position = request.json.get("position")
    status = request.json.get("status", False)

    if position in sol_ctl:
        if emergency_stop["status"] == False:
            sol_ctl[position]["status"] = status
            sol_cmd = f"{sol_ctl['top']['status']} {sol_ctl['bottom']['status']}"
            client.publish(MQTT_SOL_CMD, sol_cmd)
            print(sol_cmd)  
        return jsonify({"message": f"Soleniod {position.upper()} TOGGLED!", "status": sol_ctl[position]["status"]})
    else:
        return jsonify({"message": "Invalid solenoid position!"}), 400
    
@app.route("/gantry-ctl", methods=["POST"])
def handle_gantry():
    global gantry_ctl
    position = request.json.get("position")
    status = request.json.get("status", False)

    gantry_cmd = f"{gantry_ctl['top']['status']} {gantry_ctl['bottom']['status']}"

    

    if position in gantry_ctl:
        if emergency_stop["status"] == False:
            gantry_ctl[position]["status"] = status
            if position == 'top':
                gantry_cmd = f"{gantry_ctl['top']['status']} STOP"
            if position == 'bottom':
                gantry_cmd = f"STOP {gantry_ctl['bottom']['status']}"
            client.publish(MQTT_GANTRY_CMD, gantry_cmd)
            print(gantry_cmd)
        return jsonify({"message": f"Gantry {position.upper()} TOGGLED!", "status": gantry_ctl[position]["status"]})
    else:
        return jsonify({"message": "Invalid gantry position!"}), 400

@app.route("/npk-results", methods=["POST"])
def get_npk():
    global npk_results, ser
    
    # Initialize and open the serial connection if not already open
    if not ser.is_open:
        init_serial()
        ser.open()

    # Get new sensor values by sending the query and reading the response
    nitrogen, phosphorus, potassium = get_npk_values()

    if nitrogen is not None:
        # Update global results with the new sensor readings
        npk_results = {"n": nitrogen, "p": phosphorus, "k": potassium}
        message = (
            f"NPK SENSOR VALUES:\n"
            f"Nitrogen: {npk_results['n']}  |  "
            f"Phosphorus: {npk_results['p']}  |  "
            f"Potassium: {npk_results['k']}"
        )

        event_log.append({
            "type": "npk",
            "message": message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    else:
        message = "Failed to read NPK values"
    
    return jsonify({"message": message})
    # return jsonify({"message": f"NPK SENSOR VALUES:\nNitrogen: {npk_results["n"]}  |  Phosphorus: {npk_results["p"]}  | Potassium: {npk_results["k"]}"})

@app.route("/mode-ctl", methods=["POST"])
def handle_mode():
    global mode_ctl

    mode_cmd = f"{mode_ctl['status']}"

    client.publish(MQTT_MODE_CMD, mode_cmd)

    mode_ctl["status"] = request.json.get("status", False)
    return jsonify({"message": "MODE CHANGED!", "status": mode_ctl["status"]})



# MQTT Callback Functions ------------------------------------------------------------------
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected to broker with result code: " + str(rc))
        client.subscribe("plantPod1/data")
        client.subscribe("plantPod2/data")
        client.subscribe("plantPod3/data")
        client.subscribe("plantPod4/data")
        #client.subscribe("NPKS/data")
    else:
        print(f"Failed to connect, return code {rc}")

# Get message then save in the variable
def on_message(client, userdata, msg):
    global sensor_data
    try:
        if (msg.topic in MQTT_PLANTPOD):
            new_data = json.loads(msg.payload.decode())  # Parse JSON from ESP32
            sensor_data.update(new_data)  # Update shared sensor data
            print(f"Updated Sensor Data: {sensor_data}")
        elif (msg.topic == MQTT_TANK):
            new_data = json.loads(msg.payload.decode())
            tank_state.update(new_data)

            
            now = datetime.now()

            if new_data.get("status") == "LOW" and last_low_alert != "LOW":
                global last_low_water_event
                if last_low_water_event is None or (now - last_low_water_event) > timedelta(minutes=10):
                    event_log.append({
                        "type": "water",
                        "message": f"🚨 Tank Water LOW",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    last_low_water_event = now
                    last_low_alert = "LOW"

            elif new_data.get("status") == "OK":
                last_low_water_event = None
                last_low_alert = "OK"

    except json.JSONDecodeError:
        print("Error decoding JSON")
    except Exception as e:
        print(f"Error handling message on topic {msg.topic}: {e}")

# Used to send values for system control
def publish_mqtt(topic, message):
    if client.is_connected():
        result = client.publish(topic, message)
        status = result.rc  # Result code: 0 = Success, 1 = No Connection, etc.
        if status == 0:
            print(f"MQTT Published to {topic}: {message}")
        else:
            print(f"MQTT Publish failed for {topic}: {message}, Status Code: {status}")
    else:
        print(f"MQTT Client Not Connected - Failed to send: {topic} -> {message}")

# Start MQTT in a separate thread
def mqtt_thread():
    global client 
    client.on_connect = on_connect
    client.on_message = on_message
    #client.publish = publish_mqtt  
    client.connect("localhost", 1883, 60)
    client.loop_forever()

# NPK USB Code -----------------------------------------------------------------------------
# Used for communicating via usb to the NPK sensor
#   Changes made for windows vs Pi ('COM4' or '/dev/ttyACM0')
def init_serial():
    global ser
    ser.port = '/dev/tty/ACM0'           
    ser.baudrate = 9600         # Baud rate
    ser.stopbits = serial.STOPBITS_ONE
    ser.bytesize = serial.EIGHTBITS
    ser.parity = serial.PARITY_NONE
    ser.rtscts = 0          
    return ser

# Sends request to the npk sensor for values
def get_npk_values():
    ser.write(npk_query)  # Send MODBUS query
    time.sleep(0.15)  # Wait for the response

    # Read the response (expected length is 11 bytes)
    response = ser.read(11)
    print("Raw Response:", response.hex())  # Debugging: Print raw hex response

    # Validate response format
    if len(response) == 11 and response[0] == 0x01 and response[1] == 0x03 and response[2] == 0x06:
        # Parse the NPK values
        nitrogen = (response[3] << 8) | response[4]  # Combine high and low bytes
        phosphorus = (response[5] << 8) | response[6]
        potassium = (response[7] << 8) | response[8]
        return nitrogen, phosphorus, potassium
    else:
        print("Invalid or incomplete response")
        return None, None, None

# AUTO Code -----------------------------------------------------------------------------
# Light functions
def is_within_light_window(on_hour, off_hour):
    now_hour = datetime.now().hour
    if on_hour < off_hour:
        return on_hour <= now_hour < off_hour
    else:
        # Handles overnight (e.g., 22 to 6)
        return now_hour >= on_hour or now_hour < off_hour

def light_control_task():
    if not mode_ctl["status"]:
        print("[AUTO] Skipping lighting - Mode is MANUAL")
        return

    for pod_id, config in plant_config.items():
        light_cfg = config["light_schedule"]

        if is_within_light_window(light_cfg["on_hour"], light_cfg["off_hour"]):
            # Match pod to correct light zone
            if pod_id == "plantPod1":
                zone = "topR"
            elif pod_id == "plantPod2":
                zone = "topL"
            elif pod_id == "plantPod3":
                zone = "bottomR"
            elif pod_id == "plantPod4":
                zone = "bottomL"
            else:
                continue  # Skip unknown pod

            # Get current light reading from sensor_data
            # light_key = "light" if pod_id == "plantPod1" else f"light{pod_id[-1]}"
            # current_light = sensor_data.get(light_key, 0)
            light_threshold = config["light_threshold"]
            # buffer = config.get("buffer", 0.2)

            intensity = light_threshold

            light_ctl[zone]["intensity"] = intensity
        else:
             # Outside schedule → only override known zones
            for pod_id in plant_config:
                if pod_id == "plantPod1":
                    light_ctl["topR"]["intensity"] = 0
                elif pod_id == "plantPod2":
                    light_ctl["topL"]["intensity"] = 0
                elif pod_id == "plantPod3":
                    light_ctl["bottomR"]["intensity"] = 0
                elif pod_id == "plantPod4":
                    light_ctl["bottomL"]["intensity"] = 0

    # Build full light control string
    light_cmd = f"{light_ctl['topR']['intensity']} {light_ctl['topL']['intensity']} {light_ctl['bottomR']['intensity']} {light_ctl['bottomL']['intensity']}"
    client.publish(MQTT_LIGHT_CMD, light_cmd)
    print(f"[AUTO] Light Command Sent: {light_cmd}")

# Water functions
def watering_check_task():
    if not mode_ctl["status"]:
        print("[AUTO] Skipping watering - Mode is MANUAL")
        return

    for pod_id, config in plant_config.items():
        moist_key = "moisture" if pod_id == "plantPod1" else f"moisture{pod_id[-1]}"
        current_moisture = sensor_data.get(moist_key, 0)
        threshold = config["moisture_threshold"]
        buffer = config.get("buffer", 0.2)
        min_required = threshold * (1 - buffer)

        if current_moisture < min_required and pod_id not in list(watering_queue.queue):
            print(f"[AUTO] {pod_id} needs water (moisture={current_moisture})")
            watering_queue.put(pod_id)

def watering_queue_handler():
    global currently_watering

    while True:
        if not mode_ctl["status"]:
            time.sleep(1)
            continue  # Do nothing if Auto Mode is off

        if not currently_watering and not watering_queue.empty():
            pod_id = watering_queue.get()
            currently_watering = True

            print(f"[AUTO] Watering {pod_id}")
            water_pod(pod_id)

            duration = plant_config[pod_id]["watering_duration_sec"]
            time.sleep(duration)

            # Turn off pump + solenoids
            client.publish(MQTT_PUMP_CMD, "False")
            client.publish(MQTT_SOL_CMD, "False False")
            currently_watering = False

        time.sleep(1)

def water_pod(pod_id):
    # Determine solenoid and gantry position
    if pod_id == "plantPod1":
        sol_cmd = "True False"
        gantry_cmd = "False STOP"
    elif pod_id == "plantPod2":
        sol_cmd = "True False"
        gantry_cmd = "True STOP"
    elif pod_id == "plantPod3":
        sol_cmd = "False True"
        gantry_cmd = "STOP False"
    elif pod_id == "plantPod4":
        sol_cmd = "False True"
        gantry_cmd = "STOP True"
    else:
        print(f"[AUTO] Unknown pod: {pod_id}")
        return

    if mode_ctl["status"]:
        # Step 1: Move gantry
        print(f"[AUTO] Moving gantry for {pod_id}: {gantry_cmd}")
        client.publish(MQTT_GANTRY_CMD, gantry_cmd)

    # Step 2: Allow time for gantry to move 
    time.sleep(15)  # tune this based on how fast the gantry moves ***

    
    if mode_ctl["status"]:
        # Step 3: Open solenoid
        print(f"[AUTO] Opening solenoid: {sol_cmd}")
        client.publish(MQTT_SOL_CMD, sol_cmd)

        # Step 4: Allow solenoid to open 
        time.sleep(0.5)
        # Step 5: Start pump
        print(f"[AUTO] Starting pump")
        client.publish(MQTT_PUMP_CMD, "True")

# Schedule functions
def setup_auto_schedules():
    schedule.every(1).seconds.do(light_control_task)
    schedule.every(30).seconds.do(watering_check_task)

def stop_all_schedules():
    schedule.clear()  # Cancels all registered jobs
    with watering_queue.mutex:
        watering_queue.queue.clear()
    print("[AUTO] All scheduled tasks cleared.")

def mode_monitor_thread():
    auto_active = False

    while True:
        if mode_ctl["status"] and not auto_active:
            # Switch to AUTO
            setup_auto_schedules()
            auto_active = True
            print("[AUTO] Auto Mode ENABLED")

        elif not mode_ctl["status"] and auto_active:
            # Switch to MANUAL
            stop_all_schedules()
            auto_active = False
            print("[AUTO] Auto Mode DISABLED")

        schedule.run_pending()
        time.sleep(1)


# APP code ------------------------------------------------------------------------------
# Saving this for later dont worry about it
#def log_watering_event(pod_id):
    #now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #print(f"[LOG] {now} – Watered {pod_id}")

@app.route("/notifications", methods=["GET"])
def get_notifications():
    #print("Headers:", dict(request.headers))
    client_key = request.headers.get("X-API-Key")
    if client_key != API_KEY:
        #print("Unauthorized access attempt")
        return jsonify({"error": "Unauthorized"}), 401
    
    return jsonify(event_log[::-1])  # reverse = newest first

@app.route("/notifications", methods=["DELETE"])
def clear_notifications():
    client_key = request.headers.get("X-API-Key")
    if client_key != API_KEY:
        #print("Unauthorized access attempt")
        return jsonify({"error": "Unauthorized"}), 401
    event_log.clear()
    return jsonify({"message": "All notifications cleared!"})


@app.route("/notifications/<int:index>", methods=["DELETE"])
def delete_notification(index):
    client_key = request.headers.get("X-API-Key")
    if client_key != API_KEY:
        #print("Unauthorized access attempt")
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        event_log.pop(index)
        return jsonify({"message": f"Notification {index} deleted!"})
    except IndexError:
        return jsonify({"error": "Notification not found"}), 404

def trigger_event():
    event_log.append({
        "type": "npk",
        "message": "message",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    time.sleep(20)

    event_log.append({
        "type": "water",
        "message": f"🚨 Tank Water LOW",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    event_log.append({
        "type": "npk",
        "message": "message",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    time.sleep(0.5)

    event_log.append({
        "type": "npk",
        "message": "message",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    

@app.route("/get-pod-data", methods=["GET"])
def get_pod_data():
    #print("Flask received request for /get-pod-data")
    client_key = request.headers.get("X-API-Key")
    #print("Headers:", dict(request.headers))

    if client_key != API_KEY:
        print("Unauthorized access attempt")
        return jsonify({"error": "Unauthorized"}), 401
    
    current_data = {
        "pod1": {
            "temperature": sensor_data["temperature"],
            "humidity": sensor_data["humidity"],
            "moisture": sensor_data["moisture"],
            "light": sensor_data["light"]
        },
        "pod2": {
            "temperature": sensor_data["temperature2"],
            "humidity": sensor_data["humidity2"],
            "moisture": sensor_data["moisture2"],
            "light": sensor_data["light2"]
        },
        "pod3": {
            "temperature": sensor_data["temperature3"],
            "humidity": sensor_data["humidity3"],
            "moisture": sensor_data["moisture3"],
            "light": sensor_data["light3"]
        },
        "pod4": {
            "temperature": sensor_data["temperature4"],
            "humidity": sensor_data["humidity4"],
            "moisture": sensor_data["moisture4"],
            "light": sensor_data["light4"]
        }
    }
    return jsonify(current_data)

    



# Main Code -----------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        # Start MQTT in a separate thread
        threading.Thread(target=mqtt_thread, daemon=True).start()
        threading.Timer(1, open_browser).start()
        threading.Thread(target=watering_queue_handler, daemon=True).start()
        threading.Thread(target=mode_monitor_thread, daemon=True).start()
        
        app.run(host="0.0.0.0", port=5000, debug=True)
        
        
    except KeyboardInterrupt:
        print("Shutting down...")
