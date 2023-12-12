import boto3
import botocore
import serial
from time import sleep, time
from datetime import datetime

# AWS SETUP
region = "us-east-2"
accessKeyId = "AKIA5HSVJ3PMIMSZCQ76"
secretAccessKey = "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"
dynamodb = boto3.resource('dynamodb', aws_access_key_id=accessKeyId, aws_secret_access_key=secretAccessKey, region_name=region)

# Initialize serial connection to Arduino
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

# Constant for the maximum allowed water command interval (6 hours)
MAX_WATER_INTERVAL = 6 * 60 * 60  # 6 hours in seconds

variables = {}
lastWaterTime = time()

# Constants for dirt moisture range
MIN_DIRT_MOISTURE = 520
MAX_DIRT_MOISTURE = 840

def defaultVariables():
    default_dict = {
        "light": {"weight": 0.0, "minval": 0, "maxval": 1},
        "dirtmoisture": {"weight": 0.0, "minval": 0, "maxval": 1},
        "temp": {"weight": 0.0, "minval": 0, "maxval": 1},
        "humidity": {"weight": 0.0, "minval": 0, "maxval": 1},
        "global": {
            "forcewater": False,
            "intervaltime": 60,
            "mintime": 86400,
            "maxtime": 259200
        }
    }
    return default_dict

def readVariables():
    tableVariables = dynamodb.Table("Variables")
    dict = {}
    try:
        for label in defaultVariables().keys():
            response = tableVariables.get_item(Key={"label": label})
            if "Item" in response:
                dict[label] = response["Item"]

        tableVariables.update_item(
            Key={"label": "global"},
            UpdateExpression="set forcewater = :val",
            ExpressionAttributeValues={":val": False},
            ReturnValues="UPDATED_NEW"
        )
    except Exception as e:
        print("ERROR COLLECTING VARIABLES")
        print(e)
        return variables
    return dict

def writeData(dirtmoisture=0, light=0, temp=0, humidity=0, watered=False):
    tableData = dynamodb.Table("Data")
    try:
        response = tableData.get_item(Key={"id": -1})
        newID = response["Item"]["max"] + 1
        timeString = datetime.now().strftime("%Y-%m-%d %H:%M")

        tableData.put_item(Item={
            "id": newID,
            "time": timeString,
            "dirtmoisture": dirtmoisture,
            "light": light,
            "temp": temp,
            "humidity": humidity,
            "watered": watered
        })

        tableData.put_item(Item={
            "id": -1,
            "max": newID
        })
    except botocore.exceptions.ClientError as e:
        print(f"ClientError in writeData: {e}")
    except botocore.exceptions.BotoCoreError as e:
        print(f"BotoCoreError in writeData: {e}")
    except Exception as e:
        print(f"ERROR in writeData: {e}")
        print("Unexpected error in writeData: Float types are not supported. Use Decimal types instead.")

def readSensors():
    if arduino.in_waiting > 0:
        line = arduino.readline().decode('utf-8').rstrip()
        # Assuming Arduino sends data in 'value1,value2,value3,value4' format
        values = line.split(',')
        if len(values) == 4:
            return {
                "dirtmoisture": round((int(values[1]) - MIN_DIRT_MOISTURE) / (MAX_DIRT_MOISTURE - MIN_DIRT_MOISTURE) * 100),
                "light": int(values[0]),
                "temp": int(float(values[2])) - 5,  # Reduce temperature by 5 degrees
                "humidity": round(float(values[3]) * 0.8)  # Reduce humidity readings by 20% and round to the nearest whole number
            }
    return None

def water():
    global lastWaterTime
    current_time = time()
    if current_time - lastWaterTime >= MAX_WATER_INTERVAL:
        try:
            arduino.write("WATER\n".encode())  # Sending the command to the Arduino
            print("Sent water command to Arduino")
            lastWaterTime = current_time  # Update the lastWaterTime
        except Exception as e:
            print("Error sending water command:", e)

def waterAlgorithm(data):
    global lastWaterTime
    weight, max_val, current = algorithmHelper("light", data)

    light_percent = weight * (1 - ((max_val - current) / max_val))

    weight, max_val, current = algorithmHelper("dirtmoisture", data)
    dirt_percent = weight * (1 - ((max_val - current) / max_val))

    weight, max_val, current = algorithmHelper("temp", data)
    temp_percent = weight * ((max_val - current) / max_val)

    weight, max_val, current = algorithmHelper("humidity", data)
    humidity_percent = weight * (1 - ((max_val - current) / max_val))

    total_percent = dirt_percent + light_percent + temp_percent + humidity_percent
    max_time = int(variables["global"]["maxtime"])
    min_time = int(variables["global"]["mintime"])
    dirt_current = float(data["dirtmoisture"])
    emergency_min_val = 45  # Adjusted emergency minimum dirt moisture level
    delay = (max_time - min_time) * (1 - total_percent) + min_time
    do_standard_water = (lastWaterTime + delay) <= time()
    do_emergency_water = ((lastWaterTime + min_time) > time()) and (dirt_current <= emergency_min_val)
    do_force_water = variables["global"]["forcewater"]
    print(" ")
    print("Last Water Time:", lastWaterTime)
    print("Delay:", delay)
    print("Time + Delay:", lastWaterTime + delay)
    print("Current Time:", time())
    if do_standard_water or do_emergency_water or do_force_water:
        lastWaterTime = time()
        return True
    else:
        return False

def algorithmHelper(label, data):
    return float(variables[label]["weight"]), float(variables[label]["maxval"]), float(data[label])

def loop():
    global variables
    variables = defaultVariables()  # Initialize with default values
    while True:
        updated_variables = readVariables()
        if updated_variables:  # Update only if readVariables() is successful
            variables = updated_variables

        sleep(int(variables["global"]["intervaltime"]))
        sensorReadings = readSensors()

        if sensorReadings:  # Check if sensorReadings is not None
            sensorReadings["watered"] = waterAlgorithm(sensorReadings)
            print("\nSensor Readings:")
            print(f"Dirt Moisture: {sensorReadings['dirtmoisture']}%")  # Output dirt moisture as a percentage
            print(f"Light Level: {sensorReadings['light']}")  # Changed output label
            print(f"Temperature: {sensorReadings['temp']}°F")  # Reduced temperature by 5 degrees
            print(f"Humidity: {sensorReadings['humidity']}%")  # Rounded humidity to whole number
            print(f"Watered: {sensorReadings['watered']}")
            if sensorReadings["watered"]:
                water()
            writeData(**sensorReadings)
        else:
            print("No sensor readings available.")

if __name__ == "__main__":
    loop()
