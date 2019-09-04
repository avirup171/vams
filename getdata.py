import obd
import time
import paho.mqtt.client as paho
import json

obdjson={}
jstemp={}
mqtt_topic=""
client = paho.Client()

## MQTT
def on_connect(client, userdata, flags, rc):
    print(mqtt_topic)
    client.subscribe(mqtt_topic,qos=1)
    print("Connected")

def on_publish(client, userdata, mid):
    print("mid: "+str(mid))


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def init_mqtt(client,device_type,device_id,mqtt_host,mqtt_port,mqtt_topic):
    jstemp['device_type']=device_type
    jstemp['device_id']=device_id
    client.on_connect = on_connect  
    client.on_publish = on_publish
    client.on_subscribe=on_subscribe
    client.connect(mqtt_host, int(mqtt_port))
    print(mqtt_host)
    #return 0

## OBD

def init_connection(baud_rate,com_port,fast):
    connection = obd.Async(com_port,baudrate=baud_rate, fast=fast)
    connection.watch(obd.commands.RPM, callback=new_rpm)
    connection.watch(obd.commands.SPEED, callback=new_speed)
    connection.watch(obd.commands.COOLANT_TEMP, callback=new_coolant_temperature)
    connection.watch(obd.commands.THROTTLE_POS, callback=new_throttle_position)
    connection.start()
    print("hello")

#RPM
def new_rpm(r):
    rpmValue=r.value.magnitude
    rpm_flag=1
    obdjson["rpm"]=rpmValue
#SPEED
def new_speed(r):
    #client.publish(mqtt_topic, qos=0)    
    speed_flag=1
    obdjson["speed"]=r.value.magnitude
    jstemp["telemetry_data"]=obdjson
    json_temp = json.dumps(jstemp)
    print(obdjson)
    client.publish(mqtt_topic, str(obdjson), qos=0)
        
#COOLANT TEMPERATURE
def new_coolant_temperature(r):
    coolant_flag=1
    obdjson["coolant_temp"]=r.value.magnitude
#Throttle position
def new_throttle_position(r):
    throttle_flag=1
    obdjson["throttle_position"]=r.value.magnitude

def main():
    global filename, debug_message, mqtt_topic
    with open('mqtt_config.json') as json_data_file:
        data = json.load(json_data_file)
    mqtt_topic=data['mqtt_topic']
    print(mqtt_topic)
    init_mqtt(client,data['device_type'],data['device_id'],data['mqtt_host'],data['mqtt_port'],data['mqtt_topic'])
    #client.loop_start()
    init_connection(data['baud_rate'],data['com_port'],'fast')
    print("In main thread")
    client.loop_forever()

if __name__=='__main__':
    main()
    