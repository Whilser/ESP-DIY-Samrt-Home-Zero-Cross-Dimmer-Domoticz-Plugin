#
#           ESP Smart Home Plugin for Domoticz
#           Version 0.1.0
#
#

"""
<plugin key="ESPSmartHome" name="Espressif Systems (ESP32, ESP8266) Smart Home" author="Whilser" version="0.1.0" wikilink="" externallink="">
    <description>
        <h2>ESP Smart Home device </h2><br/>
        <h3>Configuration</h3>
        Enter Device ID of your ESP Smart Home device. If you do not know the Device ID, just leave Device ID field defaulted 0, <br/>
        this will start discover for your ESP Smart Home devices. Go to the log, it will display the found ESP Smart Home devices and the Device ID you need. <br/>
        The Scene parameter creates a selector of the 4 dimmer lamp scenes.  Set the scene parameter "show" to display scenes, otherwise set to "hide". <br/>

    </description>
    <params>
        <param field="Mode1" label="Device ID" width="300px" required="true" default="0"/>
        <param field="Mode2" label="Scenes" width="75px">
            <options>
                <option label="Show" value="Show" default="True" />
                <option label="Hide" value="Hide" />
            </options>
        </param>
        <param field="Mode3" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="True" />
            </options>
        </param>
    </params>
</plugin>
"""

import os
import sys
import os.path
import json
import socket

import Domoticz

class BasePlugin:

    UNIT_LAMP = 1
    UNIT_SCENES = 2
    UNIT_TEMPERATURE = 3

    hardware = ''
    nextTimeSync = 0
    discovered = False
    id = 1
    IP = ''

    def __init__(self):
        #self.var = 123
        return

    def onStart(self):
        Domoticz.Debug("onStart called")
        if Parameters['Mode3'] == 'Debug': Domoticz.Debugging(1)

        if Parameters['Mode1'] == '0':
            self.discover()
            return

        self.loadConfig()
        if (self.hardware == 'ZCACD1'): self.createZCDimmer()

        self.nextTimeSync = 0

        DumpConfigToLog()
        Domoticz.Heartbeat(20)

    def onStop(self):
        Domoticz.Debug("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")

    def onCommand(self, Unit, Command, Level, Color):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level)+ ", Color: "+str(Color))

        if Unit == self.UNIT_SCENES:
            self.HandleScenes(Level)
            return

        Level = max(min(Level, 100), 1)
        if not self.discover(Parameters['Mode1']): return

        try:

            if Command == 'On':
                command = {"id": self.id, "method": "set_state","state": "ON"}
                reply = self.sendCommand(json.dumps(command))

                if reply["state"] == 'ON': Devices[Unit].Update(nValue=1, sValue='On', TimedOut = False)

            elif Command == 'Off':
                command = {"id": self.id, "method": "set_state","state": "OFF"}
                reply = self.sendCommand(json.dumps(command))

                if reply["state"] == 'OFF': Devices[Unit].Update(nValue=0, sValue='Off', TimedOut = False)
                if self.UNIT_SCENES in Devices: Devices[self.UNIT_SCENES].Update(nValue=0, sValue='0')

            elif Command == 'Set Level':
                command = {"id": self.id, "method": "set_power", "power": Level ,"state": "ON"}
                reply = self.sendCommand(json.dumps(command))

                if reply["state"] == 'ON': Devices[Unit].Update(nValue=1, sValue=str(Level), TimedOut = False)

        except Exception as e:
            Domoticz.Error('Error send command to {0} with IP {1}. Device is not responding, check power/network connection. Errror: {2}'.format(Parameters['Name'], self.IP, e.__class__))
            Devices[Unit].Update(nValue=Devices[Unit].nValue, sValue=Devices[Unit].sValue, TimedOut = True)

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")

        if Parameters['Mode1'] == '0': return

        self.nextTimeSync -= 1

        try:
            if (self.nextTimeSync <= 0) and (self.UNIT_TEMPERATURE in Devices):
                self.nextTimeSync = 15

                if not self.discover(Parameters['Mode1']): return

                command = {"id": self.id, "method": "get_temperature"}
                reply = self.sendCommand(json.dumps(command))

                temperature = reply["temperature"]
                if ((temperature > 0) and (self.UNIT_TEMPERATURE in Devices)): Devices[self.UNIT_TEMPERATURE].Update(nValue=0, sValue=str(temperature), TimedOut = False)
                Domoticz.Debug('The temperature now is {} degrees.'.format(temperature))

            if (self.nextTimeSync <= 0) and (self.UNIT_LAMP in Devices):
                command = {"id": self.id, "method": "get_state"}
                reply = self.sendCommand(json.dumps(command))

                if (reply["state"] == "ON"):

                    if ((Devices[self.UNIT_LAMP].sValue != str(reply["power"])) or (Devices[self.UNIT_LAMP].nValue != 1) or (Devices[self.UNIT_LAMP].TimedOut == True)):
                        Devices[self.UNIT_LAMP].Update(nValue=1, sValue=str(reply["power"]), TimedOut = False)

                if (reply["state"] == "OFF"):
                    if ((Devices[self.UNIT_LAMP].sValue != str(reply["power"])) or (Devices[self.UNIT_LAMP].nValue != 0) or (Devices[self.UNIT_LAMP].TimedOut == True)):
                        Devices[self.UNIT_LAMP].Update(nValue=0, sValue=str(reply["power"]), TimedOut = False)

        except Exception as e:
            Devices[self.UNIT_LAMP].Update(nValue=Devices[self.UNIT_LAMP].nValue, sValue=Devices[self.UNIT_LAMP].sValue, TimedOut = True)
            #self.nextTimeSync = 0

    def HandleScenes(self, Level):

        if Level == 10:
            command = {"id": self.id, "method": "set_power", "power": 100 ,"state": "ON"}
            reply = self.sendCommand(json.dumps(command))
            Domoticz.Log('Message: '+json.dumps(reply))
            if (self.UNIT_LAMP in Devices): Devices[self.UNIT_LAMP].Update(nValue=1, sValue="100", TimedOut = False)

        if Level == 20:
            command = {"id": self.id, "method": "set_power", "power": 30 ,"state": "ON"}
            reply = self.sendCommand(json.dumps(command))
            Domoticz.Log('Message: '+json.dumps(reply))
            if (self.UNIT_LAMP in Devices): Devices[self.UNIT_LAMP].Update(nValue=1, sValue="30", TimedOut = False)

        if Level == 30:
            command = {"id": self.id, "method": "set_power", "power": 50 ,"state": "ON"}
            reply = self.sendCommand(json.dumps(command))
            Domoticz.Log('Message: '+json.dumps(reply))
            if (self.UNIT_LAMP in Devices): Devices[self.UNIT_LAMP].Update(nValue=1, sValue="50", TimedOut = False)

        if Level == 40:
            command = {"id": self.id, "method": "set_power", "power": 1 ,"state": "ON"}
            reply = self.sendCommand(json.dumps(command))
            Domoticz.Log('Message: '+json.dumps(reply))
            if (self.UNIT_LAMP in Devices): Devices[self.UNIT_LAMP].Update(nValue=1, sValue="1", TimedOut = False)

        if self.UNIT_SCENES in Devices:
            Devices[self.UNIT_SCENES].Update(nValue=1, sValue=str(Level))

    def loadConfig(self):
        config_Path = os.path.join(str(Parameters['HomeFolder']), self.hardware+str(Parameters["HardwareID"])+'.json')

        if os.path.isfile(config_Path):
            Domoticz.Debug('Loading config from '+config_Path)

            with open(config_Path) as json_file:
                config = json.load(json_file)

            self.IP = config['IP']
            self.deviceID = config['DeviceID']
            self.hardware = config['Hardware']

        else: self.discover(Parameters['Mode1'])

    def createZCDimmer(self):

        if self.UNIT_LAMP not in Devices:
            Domoticz.Device(Name='Dimmer lamp',  Unit=self.UNIT_LAMP, Type=244, Subtype=73, Switchtype=7, Used=1).Create()

        if ((Parameters['Mode2'] == 'Show') and (self.UNIT_SCENES not in Devices)):
            Options = { "Scenes": "|||||", "LevelNames": "Off|Bright|TV|Daily|Midnight", "LevelOffHidden": "true", "SelectorStyle": "0" }
            Domoticz.Device(Name="Scenes", Unit=self.UNIT_SCENES, Type=244, Subtype=62 , Switchtype=18, Options = Options, Used=1).Create()

        if self.UNIT_TEMPERATURE not in Devices:
            Domoticz.Device(Name="Temperature",  Unit=self.UNIT_TEMPERATURE, TypeName="Temperature", Used=1).Create()

    def sendCommand(self, jsonCommand):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((self.IP, 2000))
            s.send(jsonCommand.encode())
            data = s.recv(1024)
            s.close()
            self.id += 1

            Domoticz.Debug('Command sent: '+jsonCommand)
            Domoticz.Log('Reply received: '+data.decode())
            return json.loads(data.decode())

        except Exception as e:
            Domoticz.Log('Error send command to {0} with IP {1}. Device is not responding, check power/network connection. Errror: {2}'.format(Parameters['Name'], self.IP, e.__class__))

            for x in Devices:
                if  Devices[x].TimedOut == False: Devices[x].Update(nValue=Devices[x].nValue, sValue=Devices[x].sValue, TimedOut = True)

            self.discovered = False
            return {"state": "Error"}

    def discover(self, deviceID = None):
        if self.discovered: return True

        if len(self.IP) > 0:
            Domoticz.Debug('Loaded saved configuration.')
            Domoticz.Log('Attempt to connect to {2} device with ID: {0}, IP address: {1} '.format(self.deviceID, self.IP, self.hardware))

            if self.sendCommand(json.dumps({"id": self.id, "method": "get_state"})) == None:
                Domoticz.Log('Could not connect to {0} with IP {1}, starting discover.'.format(Parameters['Name'], self.IP))
                self.IP = ''
            else:
                self.discovered = True
                return self.discovered

        Domoticz.Debug('Starting discover with Device ID: {}.'.format(deviceID))
        self.discovered = False
        timeout = 5
        addr = '<broadcast>'
        discoveredDevice = None
        helobytes = 'discover'.encode()

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(timeout)
        s.sendto(helobytes, (addr, 1000))

        while True:
            try:
                data, addr = s.recvfrom(1024)

                reply = json.loads(data.decode())
                self.deviceID = reply["deviceID"]
                self.IP = reply["IP"]
                self.hardware = reply["hardware"]

                if deviceID is None:
                    Domoticz.Log('Discovered. Device ID: {0}, IP: {1}, Model: {2}'.format(self.deviceID, self.IP, self.hardware))

                else:
                    if self.deviceID == deviceID:
                        Domoticz.Log('Connected to device ID: {0} with IP address: {1}'.format(self.deviceID, self.IP))

                        config = {
                            "DeviceID": self.deviceID,
                            "IP": self.IP,
                            "Hardware": self.hardware
                        }

                        config_Path = os.path.join(str(Parameters['HomeFolder']), self.hardware+str(Parameters["HardwareID"])+'.json')
                        with open(config_Path, 'w') as outfile:
                            if json.dump(config, outfile, indent=4): Domoticz.Debug('Config file was saved.')

                    self.discovered = True

                    for x in Devices:
                        if  Devices[x].TimedOut == True: Devices[x].Update(nValue=Devices[x].nValue, sValue=Devices[x].sValue, TimedOut = False)

                    return self.discovered

            except socket.timeout:
                Domoticz.Debug('Discovery done')
                if ((deviceID is not None) and (self.discovered == False)):
                    Domoticz.Error('Could not discover with Device ID = {0}. Check power/network/Device ID.'.format(deviceID))
                    self.IP = ''

                    for x in Devices:
                        if  Devices[x].TimedOut == False: Devices[x].Update(nValue=Devices[x].nValue, sValue=Devices[x].sValue, TimedOut = True)

                return self.discovered
            except Exception as ex:
                Domoticz.Error('Error while reading discover results: {0}'.format(ex))
                break

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
        Domoticz.Debug("Device TimedOut: " + str(Devices[x].TimedOut))
    return
