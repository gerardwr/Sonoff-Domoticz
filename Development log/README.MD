Development log
-------------------
This file contains a log of the current developments of the software.

Contact me if you're interested in joining forces. Any help on moving forward is welcome!

December 20, 2017
-----------------
Created V0.0.1

December 23, 2017
-----------------
Created V0.0.2

December 25, 2017
-----------------

Github repository created and version V0.0.1 and V0.0.2 published.

I'm happy with V0.0.2 "as is". But it would be more ideal if the local server would be fully integrated in the Domoticz plugin. This requires migration of the NODE server software to the Domoticz Python framework and is quite a task. I am not sure if the Domticz framework could handle this task in a good way.

December 27, 2017
--------------------------
I have not given up the dream to "one day" create a Domoticz Python plugin that will
combine the functionality of the mdopp local Sonoff server AND the Domticz plugin I 
recently created. Not yet!

I'm currently experimenting with the Python code of the Sonota server from here:

https://github.com/mirko/SonOTA

It has similar basis as the mpdopp server:
- but in Python i.o. Node
- fully focused on replacing the Sonoff firmware with the Tasmota firmware (don't want that!)
- plus testwise switching Sonoff ON/OFF at start
- config of Sonoff and serving Sonoff included in code
- minus control via HTTP (now used in the Domoticz plugin V0.0.1 and V0.0.2)

Status of my experiment at this point in time:
- deleted all "Tasmota" uploading from the code
- Sonoff config is working OK
- Sonoff server working OK
- Sonoff registering working OK
- Sonoff testwise ON/OFF switch at "boot" working
- use of Sonoff hardware button is reported to server

In essence it's now a full working environment to config and serve Sonoff devices, but without a way to control the environment and the Sonoff's in it. In combination with the earlier developed Domoticz plugin this is all the functionally you need to create a fully integrated Domoticz plugin. But the remaining Sonota code is too complex to add "as is" to plugin.

So the next step could be to strip the code further and migrate the complex Sonota mechanisms to simpeler code to add to the plugin. The challenging part is replacing the Tornado webserver library by a "barebones" websocket handler.
