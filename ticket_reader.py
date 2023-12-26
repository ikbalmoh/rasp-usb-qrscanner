import evdev
from evdev import *
import threading
import time
from queue import *
import datetime
import requests
import RPi.GPIO as GPIO

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(8, GPIO.OUT)

# const
DEVICE_PATH = "/dev/input/event3"
API_URL = "http://localhost/api/ticket/"
DEVICE_NAME = "Newtologic  4010E"
QR_MASTER = "01HHYXPNR5HCNNKGZ5Q5EGXD8N"

qr_current = ""
qr_prev = ""
keycode = ""
device = None
is_busy = False

def openDoor(timeout = 1):
    global is_busy, qr_current
    qr_current = ""
    is_busy = True
    print('DOOR OPEN')
    GPIO.output(8, GPIO.LOW)
    time.sleep(timeout)
    GPIO.output(8, GPIO.HIGH)
    print('DOOR CLOSED')
    is_busy = False

def checkTicket(ticket_id):
    global qr_current, qr_prev, is_busy
    qr_current = ""
    if is_busy:
        print("DOOR IS BUSY")
        return
    if len(ticket_id) != 26:
        print("INVALID TICKET ID")
        return
    is_busy = True
    if ticket_id == QR_MASTER:
        openDoor()
        return;
    if qr_prev == ticket_id:
        print("ON CHECKING: " + ticket_id)
    else:
        qr_prev = ticket_id
        url = API_URL + ticket_id
        print("CHECKING TICKET: " + url)
        res = requests.post(url)
        print("RESPONSE ["+ str(res.status_code) +"]")
        data = res.json();
        print(data)
        if res.status_code == 200 and data['valid']:
            openDoor()
        else:
            print("INVALID TICKET")
        qr_prev = ""
        is_busy = False


# Reads barcode from "device"
def readQrCode():
    global qr_current, keycode, qr_prev, is_busy
    
    print ("Waiting QR code...")
    
    for event in device.read_loop():
        if event.type == evdev.ecodes.EV_KEY and event.value == 1:
            keycode = categorize(event).keycode
            if keycode == 'KEY_ENTER':
                # uploader.register(qr_current)
                print('QR CODE READED: ' + qr_current)
                if is_busy:
                    qr_current = ""
                else:
                    checkTicket(qr_current)
            else:
                qr_current += keycode[4:]
            

def find_device():
    print("Detecting scanner")
    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
    
    for d in devices:
        print(d.path, d.name, d.phys)
        if d.name == DEVICE_NAME:
            print('Scanner Found: ' + d.path)
            return d
    print('Scanner Not Found!')
    return None

GPIO.output(8, GPIO.HIGH)
# Find device...
device = find_device()
if device is None:
  print("Unable to find scanner")
else:
  readQrCode()
  