#!/usr/local/bin/python

#############################################################
#   Karelia library, by PouncySilverkitten                  #
#   github.com/PouncySilverkitten/karelia                   #
#                                                           #
#############################################################

from websocket import create_connection
import json, time, sys

botName = ""
startTime = time.time()
startDate = time.strftime("%Y-%m-%d %H:%M:%S")
paused = False
shortHelp = "This bot has not had a help message specified."
helpMessage = ["This bot has not had a help message specified. This message was generated automatically by the karelia.py library."]
room = ""
lastMessage = ""

def changeNick(nick):
    global room
    room.send(json.dumps({"type": "nick","data": {"name":nick}}))

def getUptime():
    global startTime
    timeNow = time.time()

    updays = 0
    uphours = 0
    upminutes = 0
    upseconds = 0

    upticks = timeNow - startTime
    while upticks > 86400:
        updays += 1
        upticks -= 86400
    while upticks > 3600:
        uphours += 1
        upticks -= 3600
    while upticks > 60:
        upminutes += 1
        upticks -= 60

    uptime = startDate + " (" + str(updays) + " days " + str(uphours) + " hours " + str(upminutes) + " minutes)"
    return uptime

def send(message,parent=''):
    global paused
    global room
    if not paused:
        room.send(json.dumps({'type': 'send', 'data': {'content': message, 'parent': parent}}))
    
def connectTo(roomName):
    global room
    global botName
    room = create_connection("wss://euphoria.io/room/"+roomName+"/ws")
    room.send(json.dumps({"type": "nick","data": {"name":botName}}))
    return(room)

def disconnect(room):
    room.close()

def parse():
    global room
    global paused
    global botName
    global lastMessage

    try:
        incoming = room.recv()
        
        if lastMessage != incoming:
            lastMessage = incoming

            packet = json.loads(incoming)

            if packet["type"] == "ping-event":
                room.send(json.dumps({'type': 'ping-reply', 'data': {'time': packet['data']['time']}}))

            elif packet['type'] == "send-event":
                
                if packet['data']['content'] == '!ping':
                    send('Pong!', packet['data']['id'])
                elif packet['data']['content'] == '!ping @' + botName:
                    send('Pong!',packet['data']['id']) 
         
                elif packet['data']['content'] == '!uptime @' + botName:
                    uptime = getUptime()
                    send('/me has been up since ' + uptime,packet['data']['id'])

                elif packet['data']['content'] == '!pause @' + botName:
                    send('/me has been paused',packet['data']['id'])
                    paused = True
                elif packet['data']['content'] == '!unpause @' + botName:
                    paused = False
                    send('/me has been unpaused',packet['data']['id'])
                    
                elif packet['data']['content'] == '!help @' + botName:
                    for message in helpMessage:
                        sending = message.replace('**sender**','@' + packet['data']['sender']['name'].replace(' ',''))
                        send(sending,packet['data']['id'])
                elif packet['data']['content'] == '!help':
                    send(shortHelp,packet['data']['id'])

                elif packet['data']['content'] == "!kill @" + botName:
                    send("Bot killed; will now exit.",packet['data']['id'])
                    sys.exit()

                elif packet['data']['content'] == "!antighost":
                    changeNick(botName)
                        
                else:
                    return(packet)

            handleType = ""
            if packet["type"] == "ping-event":
                handleType = "ping"
                
            return(json.loads(json.dumps({"type": "handled", 'class': handleType})))
        
    except Exception as e:
        print("Parsing error from karelia.py: " + str(e))
        return(json.dumps({"type": "error",'error':str(e)}))

def spoof(packet,spoofBot):
    global room
    global paused

    try:

        if packet['data']['content'] == '!ping @' + spoofBot:
            send('Pong!',packet['data']['id']) 
 
        elif packet['data']['content'] == '!uptime @' + spoofBot:
            uptime = getUptime()
            send('/me has been up since ' + uptime,packet['data']['id'])

        elif packet['data']['content'] == '!pause @' + spoofBot:
            send('/me has been paused',packet['data']['id'])
            paused = True
        elif packet['data']['content'] == '!unpause @' + spoofBot:
            paused = False
            send('/me has been unpaused',packet['data']['id'])
            
        elif packet['data']['content'] == '!help @' + spoofBot:
            for message in helpMessage:
                sending = message.replace('**sender**','@' + packet['data']['sender']['name'].replace(' ',''))
                send(sending,packet['data']['id'])

        elif packet['data']['content'] == "!kill @" + spoofBot:
            send("Bot killed; will now exit.",packet['data']['id'])
            sys.exit()
                
        else:
            return(packet)

        if packet["type"] == "ping-event":
            handleType = "ping"
        else:
            handleType = str(packet['data']['content'].split()[0][1:])
            
        return(json.loads(json.dumps({"type": "handled", 'class':handleType})))
        
    except Exception as e:
        print("Spoofing error from karelia.py: " + str(e))
        return(json.dumps({"type": "error",'error':str(e)}))
