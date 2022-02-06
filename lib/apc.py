import time
from telnetlib import Telnet
from prjxcore.AppLog import applog


class APCManager():
    DEVICE_MANAGER = b"1\r\n"
    OUTLET_CONTROL = b"2\r\n"
    CONTROL_OUTLET = b"1\r\n"
    IMMEDIATE_ON = b"1\r\n"
    IMMEDIATE_OFF = b"2\r\n"
    IMMEDIATE_REBOOT = b"3\r\n"
    PROMPT = b">"

    telnet = False

    def __init__(self, server, username, password, outlets):
        self.server = server
        self.username = username
        self.password = password
        self.outlets = outlets

    def __login(self, username, password):
        self.telnet.read_until(b"User Name")
        self.telnet.write(username.encode("ascii") + b"\r\n")
        self.telnet.read_until(b"Password")
        self.telnet.write(password.encode("ascii") + b"\r\n")
        self.telnet.read_until(self.PROMPT)

    def __to_main_menu(self):
        while True:
            self.telnet.write(b"\x1B")  # ESC
            response = self.telnet.read_until(self.PROMPT)
            if b"Control Console" in response:
                return

    def __read(self, watch_for, action=False):
        buffer = self.telnet.read_until(watch_for)
        applog.debug(buffer)
        if action != False:
            self.telnet.write(action)

    def control_outlet(self, outlet, method):
        self.telnet.write(self.DEVICE_MANAGER)  ## Menu - Enter Device Manager
        self.__read(self.PROMPT, self.OUTLET_CONTROL)  ## Menu - Enter Outlet Control
        self.__read(self.PROMPT, self.CONTROL_OUTLET)  ## Menu - Enter Outlet Control and Configuration
        self.__read(self.PROMPT, str(outlet).encode("ascii") + b"\r\n")  ## Specify Outlet to Control
        self.__read(self.PROMPT, self.CONTROL_OUTLET)  ## Menu - Enter Control, not configuration
        self.__read(self.PROMPT, method)  ## Specify action - i.e. Off, On or Reboot etc
        self.__read(b"Enter 'YES' to continue", b"YES\r\n")  ## Confirm
        self.__read(b"Press <ENTER>", b"\r\n")
        self.__read(self.PROMPT)
        self.__to_main_menu()

    def power(self, method):
        for outlet in self.outlets:
            try:
                self.telnet = Telnet(self.server)
                applog.debug("Opened telnet to {}".format(self.server))
                self.__login(self.username, self.password)
                applog.debug("Logged into to {}".format(self.server))
                self.control_outlet(outlet, method)
                applog.debug("Sent command for outlet {}".format(outlet))
                self.telnet.close()
                time.sleep(2)
            except:
                applog.error('Failed to power on host, on outlet {}'.format(outlet))