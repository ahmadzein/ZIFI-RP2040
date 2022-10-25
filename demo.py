import zWifiManager.wifi as wifi
f = open("key/secret.key")
key =f.read()
f.close()
wifi.Settings.apSsid = "nabokhaz"
wifi.Settings.encryptionKey = bytes(key,'utf-8')

wifi.setup_AP()
wifi.setUpServer()
wifi.http_get('https://api.thingspeak.com/update?api_key=8ZQZOA9D57SRVYIS&field1=1000')