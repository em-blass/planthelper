import boto3
import botocore
import serial
from time import sleep, time
from datetime import datetime
import threading
import queue

# AWS SETUP
region = "us-east-2"
accessKeyId = "AKIA5HSVJ3PMIMSZCQ76"
secretAccessKey = "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"
dynamodb = boto3.resource('dynamodb', aws_access_key_id=accessKeyId, aws_secret_access_key=secretAccessKey, region_name=region)

arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

MIN_DIRT_MOISTURE = 520
MAX_DIRT_MOISTURE = 840

def writeData(dirtmoisture, light, temp, humidity):
    tableData = dynamodb.Table("Data")
    try:
        response = tableData.get_item(Key={"id": -1})
        newID = response["Item"]["max"] + 1 if "Item" in response else 1
        timeString = datetime.now().strftime("%Y-%m-%d %H:%M")

        tableData.put_item(Item={
            "id": newID,
            "time": timeString,
            "dirtmoisture": dirtmoisture,
            "light": light,
            "temp": temp,
            "humidity": humidity
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

def readSensors():
    if arduino.in_waiting > 0:
        line = arduino.readline().decode('utf-8').rstrip()
        values = line.split(',')
        if len(values) == 4:
            try:
                return {
                    "dirtmoisture": round((int(values[1]) - MIN_DIRT_MOISTURE) / (MAX_DIRT_MOISTURE - MIN_DIRT_MOISTURE) * 100),
                    "light": int(values[0]),
                    "temp": int(float(values[2])),
                    "humidity": round(float(values[3]))
                }
            except ValueError as e:
                print(f"ValueError in readSensors: {e}")
                return None
    return None

def forceWaterCommand():
    try:
        arduino.write("FORCE_WATER\n".encode())
    except Exception as e:
        print("Error sending FORCE_WATER command:", e)

def check_for_command(cmd_queue):
    while True:
        cmd = input()
        cmd_queue.put(cmd)
        
def checkForceWater():
    try:
        table = dynamodb.Table("Variables")
        response = table.get_item(Key={"label": "global"})
        if 'Item' in response and response['Item']['forcewater']:
            return response['Item']['forcewater']
    except botocore.exceptions.ClientError as e:
        print(f"ClientError in checkForceWater: {e}")
    except botocore.exceptions.BotoCoreError as e:
        print(f"BotoCoreError in checkForceWater: {e}")
    except Exception as e:
        print(f"ERROR in checkForceWater: {e}")
    return False

def resetForceWater():
    try:
        table = dynamodb.Table("Variables")
        table.update_item(
            Key={"label": "global"},
            UpdateExpression="set forcewater = :val",
            ExpressionAttributeValues={":val": False}
        )
    except botocore.exceptions.ClientError as e:
        print(f"ClientError in resetForceWater: {e}")
    except botocore.exceptions.BotoCoreError as e:
        print(f"BotoCoreError in resetForceWater: {e}")
    except Exception as e:
        print(f"ERROR in resetForceWater: {e}")

def loop():
    cmd_queue = queue.Queue()
    cmd_thread = threading.Thread(target=check_for_command, args=(cmd_queue,), daemon=True)
    cmd_thread.start()

    while True:
        if checkForceWater():
            forceWaterCommand()

        if not cmd_queue.empty():
            cmd = cmd_queue.get()
            if cmd == "FORCE_WATER":
                forceWaterCommand()

        sensorReadings = readSensors()
        if sensorReadings:
            print("\nSensor Readings:")
            print(f"Dirt Moisture: {sensorReadings['dirtmoisture']}%")
            print(f"Light Level: {sensorReadings['light']}%")
            print(f"Temperature: {sensorReadings['temp']}°F")
            print(f"Humidity: {sensorReadings['humidity']}%")
            writeData(sensorReadings['dirtmoisture'], sensorReadings['light'], sensorReadings['temp'], sensorReadings['humidity'])

        if checkForceWater():
            forceWaterCommand()
            resetForceWater()

        sleep(2)

if __name__ == "__main__":
    loop()
