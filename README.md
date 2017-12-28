# Sonoff-Domoticz
A Domoticz Python Plugin for Sonoff Switches

DISCLAIMER
----------
The use of this software is free for non-commercial use. Commercial use only after explicit agreement from the developer.

Note that this software is "under construction", and must be seen as "proof of concept" and "alpha" software. The plugin was verified to run by a "couple of users" in "a couple of days" , but this is hardly a guarantee it will work in your environment.

Give it a try if you dare, but you use it at your own risk, be warned! Good luck!

What's a Sonoff switch
----------------------
A Wifi connected mains switch, controlled by an Android or IOS App.

Supplier's website : https://sonoff.itead.cc/en/


Background
----------
Sonoff Switches are default configured to be managed and controlled by a Smartphone App using a propriate Cloud service.

The functionality of the Cloud service was reverse engineered by several clever people (not me), enabling the development of a local server with similar functionality of the Cloud service. Users that do not wish to depend on a Cloud service can use their Sonoff switches i.c.w. a local server, on a Raspberry PI for example. 

Sonoff server protocol info and reverse engineering
- https://wiki.almeroth.com/doku.php?id=projects:sonoff
- https://blog.ipsumdomus.com/sonoff-switch-complete-hack-without-firmware-upgrade-1b2d6632c01
- http://blog.nanl.de/2017/05/sonota-flashing-itead-sonoff-devices-via-original-ota-mechanism/
- https://github.com/vponomarev/Sonoff-Server
- https://github.com/mdopp/simple-sonoff-server

Some more info on the use of a local Sonoff server and Domoticz
- https://www.domoticz.com/forum/viewtopic.php?f=4&t=18470&start=60#p162628

Assumptions
-----------
This Domoticz Python plugin assumes:
- that "simple-sonoff-server" from github user mdopp is installed and running (Credits to mdopp and the people that inspired him), and that the Sonoff switches are configured for the "simple-sonof-server"
- that Domoticz Beta is installed and running (Domoticz stable may have trouble running plugins)
- Sonoff types S20 and Sonoff Basic are used. Other may work, but have not been tested,

Preparation : Install simple-sonoff-server
-----------------------------------------
- Download simple-sonoff-server from : https://github.com/mdopp/simple-sonoff-server
- Adapt sonoff.config.json, setup SSID and password of your WLAN and setup IP of the machine your server is running on. I had to change "websocketPort" from 433 to 1433 (433 was probably in use already)
```
{
    "router": {
        "SSID": ".....",
        "password": "......." 
        
    },
    "server": {
        "IP": "192.168.0.28",
        "httpPort": 1081,
        "httpsPort": 1080,
        "websocketPort": 1443
    }
}
```
- Run sonoff.server.js. The server must be running all the time
- Configure your Sonoffs to use this server using sonoff.setupdevice.js. You only have to do this ONCE.

Install plugin in Domoticz
-------------------------------
- create a new subdirectory in the Domoticz/plugins directory 
- copy plugin.py file in this new Directory
- restart Domoticz so the new plugin is registered
- add the plugin in Domoticz in Setup/Hardware

![Alt text](sonoffaddplugin.png?raw=true "Title")

- Domoticz will have created the Sonoff switches automagically using default Sonofxxxxx names. You can change this name later in anything you want.

![Alt text](sonoffswitchindomoticz.png?raw=true "Title")

- Now you can use the Sonoff switches in Domoticz as any other switch. Clicking the Domoticz switch ON/OFF sends commands to the local server that switches the Sonoff’s ON/OFF.
- If the hardware button on the Sonoff switch is used for ON/OFF the new status in Domoticz is updated (this takes max 10 secs).

Version history
---------------
- V0.0.1 Inital version based on Domoticz Python plugin example "HTTP.py"
- V0.0.2 Same functionality as V0.0.1. Internal revision, processing is now compacted in onHeartbeat and onCommand callbacks

Future developments
-------------------
I'm happy "as is" with V0.02. I created the plugin "for fun" and do not really use the Sonoff switches.

But from a "user" point of view it would be more ideal if the local server would be fully integrated in the Domoticz plugin. This requires migration of the NODE server software to the Domoticz Python framework and is quite a task. I am not sure if the Domticz framework could handle this task in a good way.

Further details in the Development log here:

https://github.com/gerardwr/Sonoff-Domoticz/blob/master/Development%20log/README.MD
