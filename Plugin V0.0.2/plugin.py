# Domoticz Python plugin serving as client for local Sonoff server.
# Credits to mdopp for sharing local Sonoff server : https://github.com/mdopp/simple-sonoff-server 
# Credits to  Domticz team
#
# Author: GWR, December 2017

"""
<plugin key="Sonoff" name="Sonoff" author="gwr" version="0.0.2" externallink="www.itead.com">
    <params>
        <param field="Address" label="IP Address" width="200px" required="true" default="127.0.0.1"/>
        <param field="Port" label="Port" width="30px" required="true" default="1081"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="true" />
                <option label="Logging" value="File"/>
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import urllib.request

class BasePlugin:

    lastDevices = ""                      # will contain the last /Devices response from the Sonoff server
   
    def __init__(self):
        return

    def onStart(self):
        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)

    def onStop(self):
        Domoticz.Debug("onStop - Plugin is stopping.")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

        # update the Domticz device
        if ( str(Command).lower() == "on" ):
                UpdateDevice(Unit, 1 ,Devices[Unit].sValue)
        else:
                UpdateDevice(Unit, 0 ,Devices[Unit].sValue)

        # send command to Sonoff server to switch a Sonoff ON/OFF
        Address=Parameters["Address"]
        Port=Parameters["Port"]
        URL="http://" +Address + ":" + Port + "/devices/" + Devices[Unit].sValue + "/" + str(Command).lower()
        Domoticz.Debug("Send URL : " + URL)
        strData = str(urllib.request.urlopen(URL).read())
        Domoticz.Debug("strData_string:" + strData)
        # check if command was received OK by server
        if ('OK' in strData):
            Domoticz.Debug("Success! The local Sonoff server responded:" + strData)
        else:
            Domoticz.Debug("Problem! The local Sonoff server responded:" + strData)


    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called for connection to: "+Connection.Address+":"+Connection.Port)

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called.")
        # get device list from server
        Address=Parameters["Address"]
        Port=Parameters["Port"]
        URL="http://" +Address + ":" + Port + "/devices/"
        strData = urllib.request.urlopen(URL).read()
        Domoticz.Debug("strData:"+str(strData))
        DumpHTTPResponseToLog(strData)

        # check if there is a difference with the last response
        if (strData == self.lastDevices):
          # no processing required, so return
          Domoticz.Log("NO change in Devices")
          return
        self.lastDevices=strData

        # convert strData string to a python dictionary using eval
        strData_structure=eval(strData)

        # handle all switches provided by the local Sonoff server
        for Switch in strData_structure:
            sw_id=Switch["id"]
            sw_state=Switch["state"]
            sw_model=Switch["model"]
            sw_version=Switch["version"]
            Domoticz.Log("Sonoff switch: id=" + str(sw_id) + " state=" + str(sw_state) + " model=" + str(sw_model) + " version=" + str(sw_version))

            # compose Domoticz switch name, can later be changed in GUI
            sw_name="Sonoff"+str(sw_id)

            # display all devices in Log
            DumpConfigToLog()

            # check the Sonoff id (like 100017aec6) with the sValue of existing Domoticz devices
            deviceFound = False
            for Device in Devices:
                if (Devices[Device].sValue == sw_id):
                    deviceFound = True
                    sw_unit=Device

            if (deviceFound == True):
                # existing device
                Domoticz.Debug(sw_name + " is existing as Unit " + str(sw_unit))
                Domoticz.Debug("Existing Sonoff switch updated from : id=" + str(sw_id) + " state=" + str(sw_state) + " model=" + str(sw_model) + " version=" + str(sw_version))
            else:
                # unknown device
                Domoticz.Debug(sw_name + " is NOT existing")
                #if NO devices defined yet then set unitnumber to 1, else set new unit number as currently max unit number + 1
                if ( len(Devices) == 0 ):
                    sw_unit=1
                else:
                    sw_unit=max(Devices)+1

                # create new device device, unit to sw_unit, nvalue to 0, sValue to sw_id of Sonoff (like 100017aec6), unit to sw_unit, Used=1 
                Domoticz.Device(Name=sw_name,  Unit=sw_unit, TypeName="Switch", Used=1).Create()
                UpdateDevice(sw_unit, 0 , str(sw_id))      
                Domoticz.Log("New Sonoff switch created from : id=" + str(sw_id) + " state=" + str(sw_state) + " model=" + str(sw_model) + " version=" + str(sw_version))
                Domoticz.Log("New Sonoff switch created as unit " + str(sw_unit) + "and sValue " + str(Devices[sw_unit].sValue))

            if ( str(sw_state).lower() == "on" ):
                    # command is "on", set nValue to 1
                    UpdateDevice(sw_unit, 1 ,Devices[sw_unit].sValue)            
                    Domoticz.Log("Existing Sonoff switch updated as unit " + str(sw_unit) + " and sValue " + str(Devices[sw_unit].sValue) + " with nValue=1")
            else:
                    # command is NOT "on" so it must be "off", set nValue to 0
                    UpdateDevice(sw_unit, 0 ,Devices[sw_unit].sValue)            
                    Domoticz.Log("Existing Sonoff switch updated as unit " + str(sw_unit) + " and sValue " + str(Devices[sw_unit].sValue) + " with nValue=0")


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

def LogMessage(Message):
    if Parameters["Mode6"] == "File":
        f = open(Parameters["HomeFolder"]+"http.html","w")
        f.write(Message)
        f.close()
        Domoticz.Log("File written")

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
    return

def DumpHTTPResponseToLog(httpDict):
    if isinstance(httpDict, dict):
        Domoticz.Log("HTTP Details ("+str(len(httpDict))+"):")
        for x in httpDict:
            if isinstance(httpDict[x], dict):
                Domoticz.Log("--->'"+x+" ("+str(len(httpDict[x]))+"):")
                for y in httpDict[x]:
                    Domoticz.Log("------->'" + y + "':'" + str(httpDict[x][y]) + "'")
            else:
                Domoticz.Log("--->'" + x + "':'" + str(httpDict[x]) + "'")

def UpdateDevice(Unit, nValue, sValue, AlwaysUpdate=False):    
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it 
    if (Unit in Devices):
        if ((Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue) or (AlwaysUpdate == True)):
            Devices[Unit].Update(nValue=nValue, sValue=str(sValue))
            Domoticz.Log("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")
    return

