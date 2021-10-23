## https://github.com/scls19fr/APC


## This was from https://github.com/ahribeng/apc_pdu_controller/blob/master/apc_pdu_controller/apc_pdu_controller.py
from telnetlib import Telnet
import time

username = "apc"
password = "apc"
hostname = "10.10.50.205"
outlets = [4, 5]

DEBUG = True

# Menu options
DEVICE_MANAGER = b"1\r\n"
OUTLET_CONTROL = b"2\r\n"
CONTROL_OUTLET = b"1\r\n"
IMMEDIATE_ON = b"1\r\n"
IMMEDIATE_OFF = b"2\r\n"
IMMEDIATE_REBOOT = b"3\r\n"
PROMPT = b">"

def debug_output(str):
    if DEBUG:
        print(str)


def login(t, username, password):
    t.read_until(b"User Name")
    t.write(username.encode("ascii") + b"\r\n")
    t.read_until(b"Password")
    t.write(password.encode("ascii") + b"\r\n")
    t.read_until(PROMPT)


def to_main_menu(t):
    while True:
        t.write(b"\x1B")  # ESC
        response = t.read_until(PROMPT)
        if b"Control Console" in response:
            return


def read(t, watch_for, action=False):
    buffer = t.read_until(watch_for)
    debug_output(buffer)
    if action != False:
        t.write(action)


def control_outlet(t, outlet, method):
    t.write(DEVICE_MANAGER)  ## Menu - Enter Device Manager
    read(t, PROMPT, OUTLET_CONTROL)  ## Menu - Enter Outlet Control
    read(t, PROMPT, CONTROL_OUTLET)  ## Menu - Enter Outlet Control and Configuration
    read(t, PROMPT, str(outlet).encode("ascii") + b"\r\n")  ## Specify Outlet to Control
    read(t, PROMPT, CONTROL_OUTLET)  ## Menu - Enter Control, not configuration
    read(t, PROMPT, method)  ## Specify action - i.e. Off, On or Reboot etc
    read(t, b"Enter 'YES' to continue", b"YES\r\n")  ## Confirm
    read(t, b"Press <ENTER>", b"\r\n")
    read(t, PROMPT)
    to_main_menu(t)


def do_it(hostname, username, password, outlets, method):
    try:
        for outlet in outlets:
            telnet = Telnet(hostname)
            login(telnet, username, password)
            control_outlet(telnet, outlet, method)
            telnet.close()
    except:
        response = 'Failed'


if __name__ == "__main__":
    do_it(hostname, username, password, [4, 5], IMMEDIATE_REBOOT)
