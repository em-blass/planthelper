import boto3
import serial
from time import sleep, time
from datetime import datetime
from random import randint


# AWS SETUP
region = "us-east-2"
accessKeyId = "AKIA5HSVJ3PMIMSZCQ76"
secretAccessKey = "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"
dynamodb = boto3.resource('dynamodb', aws_access_key_id=accessKeyId, aws_secret_access_key=secretAccessKey, region_name=region)

# Initialize serial connection to Arduino
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

variables = {}

lastWaterTime = time()


def defaultVariables():
    dict = {}
    for label in ["dirtmoisture", "light", "temp", "humidity"]:
        dict[label] = {}
        dict[label]["weight"] = 0
        dict[label]["minval"] = 0
        dict[label]["maxval"] = 1
    dict["dirtmoisture"]["emergencyminval"] = 0
    dict["global"] = {}
    dict["global"]["forcewater"] = False
    dict["global"]["intervaltime"] = 60
    dict["global"]["mintime"] = 86400
    dict["global"]["maxtime"] = 259200
    return dict

def readVariables():
    tableVariables = dynamodb.Table("Variables")
    dict = {}
    try:
        for label in ["dirtmoisture", "light", "temp", "humidity", "global"]:
            response = tableVariables.get_item(Key={"label": label})
            if ("Item" in response):
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
    
def writeData(dirtmoisture = 0, light = 0, temp = 0, humidity = 0, watered = False):
    tableData = dynamodb.Table("Data")
    response = tableData.get_item(Key={"id": -1})
    newID = response["Item"]["max"] + 1
    timeString = datetime.now().strftime("%Y-%m-%d %H:%M")
    tableData.put_item(Item = {
        "id": newID,
        "time": timeString,
        "dirtmoisture": dirtmoisture,
        "light": light,
        "temp": temp,
        "humidity": humidity,
        "watered": watered
    })
    
    tableData.put_item(Item = {
        "id": -1,
        "max": newID
    })
    
def readSensors():
    if arduino.in_waiting > 0:
        line = arduino.readline().decode('utf-8').rstrip()
        # Assuming Arduino sends data in 'value1,value2,value3,value4' format
        values = line.split(',')
        if len(values) == 4:
            return {
                "dirtmoisture": int(values[0]),
                "light": int(values[1]),
                "temp": int(values[2]),
                "humidity": int(values[3])
            }
    return None

def water():
    try:
        arduino.write("WATER\n".encode())  # Sending the command to the Arduino
        print("Sent water command to Arduino")
    except Exception as e:
        print("Error sending water command:", e)

def waterAlgorithm(data):
    global lastWaterTime
    weight, max, current = algorithmHelper("dirtmoisture", data)
    
    dirtPercent = weight * (1 - ((max - current) / max))
    
    weight, max, current = algorithmHelper("light", data)
    lightPercent = weight * (1 - ((max - current) / max))
    
    weight, max, current = algorithmHelper("temp", data)
    tempPercent = weight * ((max - current) / max)
    
    weight, max, current = algorithmHelper("humidity", data)
    humidityPercent = weight * (1 - ((max - current) / max))
    
    totalPercent = dirtPercent + lightPercent + tempPercent + humidityPercent
    maxTime = int(variables["global"]["maxtime"])
    minTime = int(variables["global"]["mintime"])
    dirtCurrent = float(data["dirtmoisture"])
    emergencyminval = float(variables["dirtmoisture"]["emergencyminval"])
    delay = (maxTime - minTime) * (1-totalPercent) + minTime
    doStandardWater = (lastWaterTime + delay) <= time()
    doEmergencyWater = ((lastWaterTime + minTime) > time()) and (dirtCurrent <= emergencyminval)
    doForceWater = variables["global"]["forcewater"]
    print("last:", lastWaterTime, "delay:", delay, "t+delay:", lastWaterTime+delay, "time", time())
    if (doStandardWater or doEmergencyWater or doForceWater):
        lastWaterTime = time()
        return True
    else:
        return False
    
    
    
def algorithmHelper(label, data):
    return float(variables[label]["weight"]), float(variables[label]["maxval"]), float(data[label])

    
    
def loop():
    global variables
    while True:
        variables = readVariables()
        sleep(int(variables["global"]["intervaltime"]))
        sensorReadings = readSensors()
        sensorReadings["watered"] = waterAlgorithm(sensorReadings)
        if (sensorReadings["watered"]):
            water()
        writeData(dirtmoisture = sensorReadings["dirtmoisture"],
                  light = sensorReadings["light"],
                  temp = sensorReadings["temp"],
                  humidity = sensorReadings["humidity"],
                  watered = sensorReadings["watered"])

if __name__ == "__main__":
    variables = defaultVariables()
    loop()
    
    
