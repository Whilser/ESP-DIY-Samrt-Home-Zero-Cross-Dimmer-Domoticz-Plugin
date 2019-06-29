# ESP DIY Samrt Home
**Domoticz plugin** for **DIY Smart Home** based on Espressif Systems (ESP32, ESP8266). **Note:** The plugin is under development. The plugin was tested with python 3.5.x and Domoticz 4.x installed on Raspberry Pi.

**Currently supported:**

- [x] DIY Smart Home AC dimmer 220V

## Flashing ESP8266 (NodeMCU)

Use [nodemcu-pyflasher](https://github.com/marcelstoer/nodemcu-pyflasher/) to flashout firmware to ESP8266 (NodeMCU)

![NodeMCU-pyflasher](https://github.com/marcelstoer/nodemcu-pyflasher/blob/master/images/gui.png)


## How to Install:

    cd domoticz/plugins
    git clone https://github.com/Whilser/ESP-DIY-Samrt-Home.git ESPSmartHome
    sudo service domoticz restart

## How to update:

    cd domoticz/plugins/ESPSmartHome
    git pull
    sudo service domoticz restart

## Domoticz configuration

To configure device just enter Device ID of your ESP Smart Home device. If you do not know the Device ID, just leave Device ID field defaulted 0, this will start discover for your ESP Smart Home devices. Go to the Domoticz log, it will display the found ESP Smart Home devices and the Device ID you need.

![Domoticz configuration](https://github.com/Whilser/ESP-DIY-Samrt-Home/raw/master/images/DomoticzConfig.png)

The plugin creates a dimmer switch and a set of scenes. **Bright** is a bright scene, **TV** is a light of 30% power, **Daily** is a half-dimmer switched on, **Midnight** is minimal lighting.

![connection diagram](https://github.com/Whilser/ESP-DIY-Samrt-Home/raw/master/images/Units.png)

## Connection diagram for ESP Smart Home DIY AC dimmer

![connection diagram](https://github.com/Whilser/ESP-DIY-Samrt-Home/raw/master/images/ESPDIYSmartHome.png)

**Control through SSH commands:**

    {"id":1, "method":"set_power", "power":"50", "state":"ON"}
    {"id":1, "method":"set_power", "power":"50", "state":"OFF"}
    {"id":1, "method":"set_state", "state":"OFF"}
    {"id":1, "method":"set_state", "state":"ON"}
    {"id":1, "method":"set_config", "SSID":"Wi-Fi SSID", "PASSWD": "PASSWORD"}
    {"id":1, "method":"set_mode", "mode":"TOGGLE_MODE"}
    {"id":1, "method":"get_temperature"}
    {"id":1, "method":"get_state"}
    {"id":1, "method":"update", "IP":"<Update Server IP>, "url":"/update/firmware.bin"}
    
 ### Connecting the device to the Wi-Fi network
 
In case of unsuccessful connection to the Wi-Fi network, the device creates an access point with an ip address 192.168.4.1. To send Wi-Fi network settings (SSID, PASSWORD) to the device, connect to the AP and send a command via SSH terminal:

    echo '{"id":1, "method":"set_config", "SSID":"Wi-Fi SSID", "PASSWD": "PASSWORD"}' | nc -w1 192.168.4.1 2000
