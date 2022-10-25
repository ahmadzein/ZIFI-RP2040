import socket
import network
import machine
import ure
import gc
import time
import json
import os
import array

class Settings:
    connect = True
    connected = False
    connectWIFI = False
    loadPages = True
    profile = {}
    ssid = ""
    key=""
    apSsid = "Setup-new-device"
    apKey="123456789"
    fail= False
    trying = 1
    MaxTries = 2
    socketFirst = True
    encryptionKey = b''

settings = Settings()

gc.collect()

NETWORK_PROFILES = 'wifi.dat'

ap = network.WLAN(network.AP_IF)

ap.active(True)

ssids = ap.scan()
ssids =  [[x.decode('utf-8'), a, b, c, d, e] for x, a,b,c,d,e in ssids]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('NEXXXT 1')

s.bind(('', 80))
print('NEXXXT 1')

s.listen(5)
print('NEXXXT 2')


def read_profiles():
    with open(NETWORK_PROFILES) as f:
        lines = f.readlines()
    for line in lines:
        ssid, password = line.strip("\n").split(";")
        settings.ssid = ssid
        settings.key = password
        do_connect(ssid,password)
    return settings.profile

def write_profiles(profiles):
    lines = []
    for ssid, password in profiles.items():
        lines.append("%s;%s\n" % (ssid, password))
    with open(NETWORK_PROFILES, "w") as f:
        f.write(''.join(lines))

def send_response(client, payload, status_code=200):
    send_header(client)
    content_length = len(payload)
    send_header(client, status_code, content_length)
    if content_length > 0:
        client.send(payload)
    client.close()
    
def check_file():
    try:
        settings.profile = read_profiles()
        settings.loadPages = False
        settings.connectWIFI = True
        return True
    except OSError:
        settings.profile = {}
        settings.loadPages = True
        settings.connectWIFI = False
        return False
    


def setup_AP():
    if(check_file()):
        return True
    ap.active(True)
    settings.connect = False
    ap.config(essid=settings.apSsid, key=settings.apKey, security=ap.WEP)
    print('Connection successful')
    print(ap.ifconfig())
    
def web_page():
    f = open("zWifiManager/staticHTML/home/"+"start.html")
    print("ch123 thinking")
    html =f.read()
    print("ch123 thinking")
    f.close()
    return html

def handle_root(client):
    f = opf = open("zWifiManager/staticHTML/setup/start.html")
    html =f.read()
    client.send(html)
    f = opf = open("zWifiManager/staticHTML/setup/js.js")
    html = f.read()
    gc.collect()
    f.close()
    client.send(html)
    gc.collect()
    f = opf = open("zWifiManager/staticHTML/setup/body.html")
    html = f.read()
    f.close()
    client.send(html)
    gc.collect()
    
    for ssid in ssids:
        gc.collect()
        html="""\
                        <tr>
                            <td colspan="2">
                                <input type="radio" name="ssid" value="{0}" />{0}
                            </td>
                        </tr>
        """.format(ssid[0])
        client.send(html)
        
    html = """\
                        <tr>
                            <td>secretKey:</td>
                            <td><input name="secretKey" type="password" /></td>
                        </tr>
                        <tr>
                            <td>Password:</td>
                            <td><input name="password" type="password" /></td>
                        </tr>
                    </tbody>
                </table>
                <p style="text-align: center;">
                    <input type="submit" value="Submit" />
                </p>
            </form>
            <p>&nbsp;</p>
            <hr />
            <h5>
                <span style="color: #ff0000;">
                    Your ssid and password information will be saved into the
                    "%(filename)s" file in your module for future usage.
                    Be careful about security!
                </span>
            </h5>
            <hr />
            <h2 style="color: #2e6c80;">
                Some useful infos: you can add notes here
            </h2>
            </body>
        </html>
    """ % dict(filename=NETWORK_PROFILES)
    client.send(html)
    client.close()
        
   

def web_page_one():
    f = open("zWifiManager/staticHTML/one/start.html")
    print("ch123 thinking")
    html =f.read()
    print("ch123 thinking")
    f.close()
    return html

def web_page_two():
    f = open("zWifiManager/staticHTML/two/start.html")
    print("ch123 thinking")
    html =f.read()
    print("ch123 thinking")
    f.close()
    return html

def send_header(client, status_code=200, content_length=None ):
    client.send('HTTP/1.1 '+str(status_code)+' OK\n')
    client.send('Content-Type: text/html\n')
    client.send('Connection: close\n\n')
    if content_length is not None:
        client.send("Content-Length: {}\r\n".format(content_length))
    client.send("\r\n")

def decryption(string):
    array = string.split('%2C')
    encodeKeyLength = len(settings.encryptionKey)-1
    encArr = []
    for index , byte in enumerate(array):
        print('ch123 byte',byte , index)
        calc = int(byte) / int(settings.encryptionKey[encodeKeyLength]);
        encArr.append(int(calc));
        encodeKeyLength = encodeKeyLength-1
        if encodeKeyLength < 0:
              encodeKeyLength = len(settings.encryptionKey)-1
    byte_array = bytearray(encArr, 'utf-8')
    print(byte_array)
    return byte_array.decode('UTF-8')

def encryption(string):
    encodeKeyLength = len(settings.encryptionKey)-1
    print('ch123',settings.encryptionKey)
    encArr = []
    for index , byte in enumerate(bytes(string,'utf-8')):
        print('ch123 byte',byte , index)
        calc = int(byte) * int(settings.encryptionKey[encodeKeyLength]);
        encArr.append(int(calc));
        encodeKeyLength = encodeKeyLength-1
        if encodeKeyLength < 0:
              encodeKeyLength = len(settings.encryptionKey)-1
    return encArr
    
    
def handle_configure(client, request):
    match = ure.search("ssid=([^&]*)&secretKey=&password=(.*)'", request)

    if match is None:
        f = open("zWifiManager/staticHTML/error/general.html")
        html =f.read()
        f.close()
        return html
     
    wifiKey = decryption(match.group(2))

    try:
        ssid = match.group(1).decode("utf-8").replace("%3F", "?").replace("%21", "!")
        password = wifiKey.decode("utf-8").replace("%3F", "?").replace("%21", "!")
    except Exception:
        ssid = match.group(1).replace("%3F", "?").replace("%21", "!")
        password = wifiKey.replace("%3F", "?").replace("%21", "!")

    if len(ssid) == 0:
        f = open("zWifiManager/staticHTML/error/general.html")
        html =f.read()
        f.close()
        return html

    connection = do_connect(ssid, password)
    if connection:
        return connection
    else:
        f = open("zWifiManager/staticHTML/error/wrong_pass.html")
        html =f.read()
        f.close()
        return html
        
        
       
        

def do_connect(ssid = settings.ssid, password = settings.key):
    try :
        ap.active(False)
        netcon = network.WLAN(network.STA_IF)
        netcon.active(True)
        time.sleep(1)
        netcon.connect(ssid, password)
        # We should have a valid IP now via DHCP
        settings.profile[ssid] = password
        write_profiles(settings.profile)
        settings.connectWIFI = False
        gc.collect()
        settings.loadPages = False
        settings.connected = True
        return True
        
    except OSError as e:
        
        settings.connected = False
        settings.trying +=1	
        if settings.trying <= settings.MaxTries:
            gc.collect()
            do_connect(ssid, password)
        else:
            settings.fail = True
            #os.remove(NETWORK_PROFILES)
            netcon.active(False)
            time.sleep(1)
            s.bind(('', 80))
            s.listen(5)
            setup_AP()
            time.sleep(1)
            settings.connected = False
            gc.collect()
            return False

def http_get(url):
    import socket
    result = '';
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    while True:
        try:
            data = s.recv(100)
            print(data)
        except:
            data = False
            print(data)
        if data:
            result += str(data, 'utf8')
            print(result)
        else:
            print("errror")
            break
    s.close()
    return result


def setUpServer():
    while (settings.connected == False):
         if(settings.connected):
             print("Stop pages....")
             break
         try:
            print("loading pages....")
            if settings.socketFirst :
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind(('', 80))
                s.listen(5)
                settings.socketFirst = False
            print("ane han")
            if gc.mem_free() < 102000:
                gc.collect()
            print("ane han 3")
            conn, addr = s.accept()
            conn.settimeout(10.0)
            request = conn.recv(1024)
            request = str(request)
            page_one = request.find('/?page_one')
            page_two = request.find('/?page_two')
            setup = request.find('/?setup')
            config = request.find('/configure')
            if(settings.fail == True):
             send_response(conn,"""\
            <html>
                <center>
                    <h1 style="color: #5e9ca0; text-align: center;">
                        <span style="color: #ff0000;">
                            ESP could not connect to WiFi network please go back and fix any mistakes.
                        </span>
                    </h1>
                    <br><br>
                    <form>
                        <input type="button" value="Go back!" onclick="history.back()"></input>
                    </form>
                </center>
            </html>
        """)
             settings.fail = False
            if page_one == 6:
                response = web_page_one()
                send_response(conn,response)
            elif page_two == 6:
                response = web_page_two()
                send_response(conn,response)
            elif config == 7:
                response = handle_configure(conn,request)
                if response == True:
                    break
                send_response(conn,response)
            elif setup == 6:
                handle_root(conn)
                
            else:
                response = web_page()
                send_response(conn,response)
         except OSError as e:
                    settings.socketFirst = True
                    setup_AP()
                    setUpServer()
                    print('Connection closed with errors', e)
                    break
                    
    print(" connected settings.connected",settings.connected)
