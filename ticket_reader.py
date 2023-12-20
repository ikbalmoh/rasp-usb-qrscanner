import evdev
from evdev import *
import threading
import time
from queue import *
import datetime

device_path = "/dev/input/event3"
current_qrcode = ""
prev_qrcode = ""
keycode = ""
device = None
device_name = "Newtologic  4010E"

def checkTicket(ticket):
    global current_qrcode, prev_qrcode
    current_qrcode = ""
    if prev_qrcode != ticket:
        prev_qrcode = ticket
        print("CHECKING TICKET: " + ticket)
    else:
        print("STILL CHECKING")


# Reads barcode from "device"
def readQrCode():
    global current_qrcode, keycode, prev_qrcode
    
    print ("Waiting QR code...")
    
    for event in device.read_loop():
        if event.type == evdev.ecodes.EV_KEY and event.value == 1:
            keycode = categorize(event).keycode
            if keycode == 'KEY_ENTER':
                # uploader.register(current_qrcode)
                print('QR CODE READED: ' + current_qrcode)
                checkTicket(current_qrcode)
            else:
                current_qrcode += keycode[4:]
            

def find_device():
    print("Detecting scanner")
    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
    
    for d in devices:
        print(d.path, d.name, d.phys)
        if d.name == device_name:
            print('Scanner Found')
            return d
        print('Scanner Not Found!')
    return None

# Find device...
device = InputDevice('/dev/input/event3')
if device is None:
  print("Unable to find scanner")
else:
  #... instantiate the uploader...
  # uploader = BarcodeUploader()
  # ... and read the bar codes.
  readQrCode()