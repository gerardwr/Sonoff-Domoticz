# Goolgle Home page example
#
# Author: Dnpwwo, 2017
#
#   Demonstrates HTTP connectivity.
#   After connection it performs a GET on  www.google.com and receives a 302 (Page Moved) response
#   It then does a subsequent GET on the Location specified in the 302 response and receives a 200 response.
#
# used as base to create Sonoff Plugin
 
"""
<plugin key="Sonoff" name="Sonoff" author="gwr" version="0.0.1" externallink="www.itead.com">
    <params>
        <param field="Address local Sonoff server " label="IP Address" width="200px" required="true" default="127.0.0.1"/>
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

    httpConn = None
    runAgain = 1
   
    def __init__(self):
        return

    def onStart(self):
        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)
        DumpConfigToLog()
        self.httpConn = Domoticz.Connection(Name="HTTP Test", Transport="TCP/IP", Protocol="HTTP", Address=Parameters["Address"], Port=Parameters["Port"])
        self.httpConn.Connect()

    def onStop(self):
        Domoticz.Log("onStop - Plugin is stopping.")

    def onConnect(self, Connection, Status, Description):
        if (Status == 0):
            Domoticz.Debug("Local Sonoff server  connected successfully.")
            sendData = { 'Verb' : 'GET',
                         'URL'  : '/devices',
                         'Headers' : { 'Content-Type': 'text/xml; charset=utf-8', \
                                       'Connection': 'keep-alive', \
                                       'Accept': 'Content-Type: text/html; charset=UTF-8', \
                                       'Host': Parameters["Address"]+":"+Parameters["Port"], \
                                       'User-Agent':'Domoticz/1.0' }
                       }
            Connection.Send(sendData)
        else:
            Domoticz.Log("Failed to connect ("+str(Status)+") to: "+Parameters["Address"]+":"+Parameters["Port"]+" with error: "+Description)

    def onMessage(self, Connection, Data):
        #DumpHTTPResponseToLog(Data)
        # expect strData like [{"id":"100017aec6","state":"on","model":"PSA-B01-GL","version":"1.5.5"},{"id":"100017aec6","state":"on","model":"PSA-B01-GL","version":"1.5.5"}]
        strData = Data["Data"].decode("utf-8", "ignore")
        Status = int(Data["Status"])
        #LogMessage(strData)

        if (Status == 200):
            # success
            Domoticz.Log("Response from local Sonoff server."+str(strData))
            self.httpConn.Disconnect()
        else:
            # problem
            Domoticz.Error("Local Sonoff server returned a status: "+str(Status))

        # convert strData string to a python dictionary using eval
        strData_structure=eval(strData)

        # handle all switches provided by the local Sonoff server
        Domoticz.Log("loop strData_structure")
        for Switch in strData_structure:
            sw_id=Switch["id"]
            sw_state=Switch["state"]
            sw_model=Switch["model"]
            sw_version=Switch["version"]
            Domoticz.Log("Sonoff switch: id=" + str(sw_id) + " state=" + str(sw_state) + " model=" + str(sw_model) + " version=" + str(sw_version))

            # compose name off switch in Domoticz, can later be changed in GUI
            sw_name="Sonoff"+str(sw_id)

            # Domoticz.Debug("Existing Devices:" + str(Devices))
            DumpConfigToLog()

            # check the Sonoff id (like 100017aec6) with the sValue of existing Domoticz devices
            deviceFound = False
            for Device in Devices:
                if (Devices[Device].sValue == sw_id):
                    deviceFound = True
                    sw_unit=Device

            if (deviceFound == True):
                # existing device
                Domoticz.Debug("Sonoff " + sw_id + " is existing as Unit " + str(sw_unit))
                Domoticz.Debug("Existing Sonoff switch updated from : id=" + str(sw_id) + " state=" + str(sw_state) + " model=" + str(sw_model) + " version=" + str(sw_version))
            else:
                # unknown device
                Domoticz.Debug("Sonoff-" + sw_id + "is NOT existing")
                #if NO devices defined yet, set unitnumber to 1, else set new unit number as currently max unit number + 1
                if ( len(Devices) == 0 ):
                    sw_unit=1
                else:
                    sw_unit=max(Devices)+1

                # create new device device, unit to sw_unit, nvalue to 0, sValue to sw_id of Sonoff (like 100017aec6), unit to sw_unit, Used=1 
                Domoticz.Device(Name=sw_name,  Unit=sw_unit, TypeName="Switch", Used=1).Create()
                UpdateDevice(sw_unit, 0 , str(sw_id))      
                Domoticz.Debug("New Sonoff switch created from : id=" + str(sw_id) + " state=" + str(sw_state) + " model=" + str(sw_model) + " version=" + str(sw_version))
                Domoticz.Debug("New Sonoff switch created as unit " + str(sw_unit) + "and sValue " + str(Devices[sw_unit].sValue))

            if ( str(sw_state).lower() == "on" ):
                    # command is "on", set nValue to 1
                    UpdateDevice(sw_unit, 1 ,Devices[sw_unit].sValue)            
                    Domoticz.Debug("Existing Sonoff switch updated as unit " + str(sw_unit) + " and sValue " + str(Devices[sw_unit].sValue) + " with nValue=1")
            else:
                    # command is NOT "on" so it must be "off", set nValue to 0
                    UpdateDevice(sw_unit, 0 ,Devices[sw_unit].sValue)            
                    Domoticz.Debug("Existing Sonoff switch updated as unit " + str(sw_unit) + " and sValue " + str(Devices[sw_unit].sValue) + " with nValue=0")


    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

        # update the Domticz device
        if ( str(Command).lower() == "on" ):
                UpdateDevice(Unit, 1 ,Devices[Unit].sValue)
        else:
                UpdateDevice(Unit, 0 ,Devices[Unit].sValue)

        # send command to Sonoff server
        Address=Parameters["Address"]
        Port=Parameters["Port"]
        URL="http://127.0.0.1:" + Port + "/devices/" + Devices[Unit].sValue + "/" + str(Command).lower()
        Domoticz.Debug("Send URL : " + URL)
        self.sonoffSend(URL)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called for connection to: "+Connection.Address+":"+Connection.Port)

    def onHeartbeat(self):
        if (self.httpConn.Connecting() or self.httpConn.Connected()):
            Domoticz.Debug("onHeartbeat called, Connection is alive.")
        else:
            self.runAgain = self.runAgain - 1
            if self.runAgain <= 0:
                self.httpConn.Connect()
                self.runAgain = 1
            else:
                Domoticz.Debug("onHeartbeat called, run again in "+str(self.runAgain)+" heartbeats.")

    def GetValue(self, arr, sKey, defValue):
        try:
            if str(sKey) in arr:
                if ( str(arr[str(sKey)]).lower() == "none" ):
                    return defValue
                else:
                    return arr[str(sKey)]
            else:
                return defValue
        except:
            return defValue

    def sonoffSend(self, URL):
        strData_string = str(urllib.request.urlopen(URL).read())
        Domoticz.Log("strData_string:" + strData_string)
        if ('OK' in strData_string):
            Domoticz.Debug("Success! The local Sonoff server responded 'OK'")
        else:
            Domoticz.Error("Problem! The local Sonoff server did not respond 'OK'")


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

