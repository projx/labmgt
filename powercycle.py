## https://github.com/scls19fr/APC
## This was from https://github.com/ahribeng/apc_pdu_controller/blob/master/apc_pdu_controller/apc_pdu_controller.py
from telnetlib import Telnet
import time
import urllib3
import logging
import requests
import os
from requests.auth import HTTPBasicAuth
from prjxcore.AppLog import applog
from pprint import pprint

hosts = {
    "esx-04" : {"fqdn" : "esx-04.prjx.uk", "outlet" : "5", "enabled" : False},
    "esx-05" : {"fqdn" : "esx-05.prjx.uk", "outlet" : "4", "enabled" : False}
}

class WebManager:
    fqdn = ""
    url = ""
    def __init__(self, fqdn):
        self.setFQDN(fqdn)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def setFQDN(self, fqdn):
        self.fqdn = fqdn
        self.url = "https://{}/ui/#/login".format(self.fqdn)

    def isWebUp(self):
        try:
            result = requests.head(self.url, verify=False, timeout=5)
            applog.info("Check {}".format(self.url))
            pprint(result.status_code)
            if result.status_code == 200:
                return True
            return False
        except requests.ConnectionError as e:
            applog.info("{} is not responding".format(self.url))
            return False

    def test_web_server(self, delay, attempts):
        result = None
        for count in range(attempts):
            try:
                print("************************************")
                print(self.url)
                result = requests.head(self.url, verify=False, timeout=5)

                ## If we get a valid response... great
                if result.status_code == 200:
                    applog.info("{} is NOW accessible, on attempt {}, total delay was {} seconds".format(self.url, count+1, count*delay))
                    time.sleep(delay)
                    return True

            ## An exception is going to happen everytime a request fails, such as timeout or rejected connection
            except Exception as e:
                applog.info("{} is not responding, please wait - attempt {} of {}, delaying {} seconds".format(self.url, count + 1, attempts, delay))
            finally:
                time.sleep(delay)

                ## If we're post exception, there will be no response, so nothing to do... else only log message if
                ## we didn't see a 200... this stop the message showing on function exit
                if result is not None:
                    if result.status_code != 200:
                        applog.info("{} is responding with HTTP {} - attempt {} of {}, delaying {} seconds".format(self.url, result.status_code, count + 1, attempts, delay))

                        result.close()

        return False

class AWXManager:
    def run(self):
        res = requests.post("https://awx.prjx.uk/api/v2/job_templates/10/launch/", verify=False,
                            auth=HTTPBasicAuth('admin', 'bXlzdXBlcmxvbmdwYXNzd29yZAo='))
        print(res.content)


class APCManager():
    DEVICE_MANAGER = b"1\r\n"
    OUTLET_CONTROL = b"2\r\n"
    CONTROL_OUTLET = b"1\r\n"
    IMMEDIATE_ON = b"1\r\n"
    IMMEDIATE_OFF = b"2\r\n"
    IMMEDIATE_REBOOT = b"3\r\n"
    PROMPT = b">"

    telnet = False

    def login(self, username, password):
        self.telnet.read_until(b"User Name")
        self.telnet.write(username.encode("ascii") + b"\r\n")
        self.telnet.read_until(b"Password")
        self.telnet.write(password.encode("ascii") + b"\r\n")
        self.telnet.read_until(self.PROMPT)

    def to_main_menu(self):
        while True:
            self.telnet.write(b"\x1B")  # ESC
            response = self.telnet.read_until(self.PROMPT)
            if b"Control Console" in response:
                return

    def read(self, watch_for, action=False):
        buffer = self.telnet.read_until(watch_for)
        applog.debug(buffer)
        if action != False:
            self.telnet.write(action)

    def control_outlet(self, outlet, method):
        self.telnet.write(self.DEVICE_MANAGER)  ## Menu - Enter Device Manager
        self.read(self.PROMPT, self.OUTLET_CONTROL)  ## Menu - Enter Outlet Control
        self.read(self.PROMPT, self.CONTROL_OUTLET)  ## Menu - Enter Outlet Control and Configuration
        self.read(self.PROMPT, str(outlet).encode("ascii") + b"\r\n")  ## Specify Outlet to Control
        self.read(self.PROMPT, self.CONTROL_OUTLET)  ## Menu - Enter Control, not configuration
        self.read(self.PROMPT, method)  ## Specify action - i.e. Off, On or Reboot etc
        self.read(b"Enter 'YES' to continue", b"YES\r\n")  ## Confirm
        self.read(b"Press <ENTER>", b"\r\n")
        self.read(self.PROMPT)
        self.to_main_menu()

    def power(self, hostname, username, password, outlets, method):
        try:
            for outlet in outlets:
                self.telnet = Telnet(hostname)
                applog.info("Opened telnet to {}".format(hostname))
                self.login(username, password)
                applog.info("Logged into to {}".format(hostname))
                self.control_outlet(outlet, method)
                applog.info("Sent command for outlet {}".format(outlet))
                self.telnet.close()
        except:
            response = 'Failed'


def main(suppress, hosts):
    """QtooL - Is a scheduler for Polling, Formatting and Sending """

    delay = 20
    attempts = 20
    # Handle flags
    show_output = False if suppress else True
    applog.setup(show_output, False)
    applog.set_enabled(True)
    applog.set_info(True)
    # applog.set_debug(True)

    for key, host in hosts.items():
        wm = WebManager(host["fqdn"])
        if wm.isWebUp() == True:
            msg = "Aborting Power-cycle - The {} Server is running, power-cycle could lead to data corruption".format(host["fqdn"])
            applog.error(msg)
            raise Exception(msg)

    for key, host in hosts.items():
        apc = APCManager()
        applog.info("Preparing power-cycle for {} on outlet {}".format( host["fqdn"], host["outlet"]))
        apc.power("10.10.50.205", "apc", "apc", host["outlet"], apc.IMMEDIATE_OFF)

    applog.info("Off cycle complete, waiting {} seconds before powering On".format(delay))
    time.sleep(delay)

    for key, host in hosts.items():
        apc = APCManager()
        applog.info("Preparing power-cycle for {} on outlet {}".format( host["fqdn"], host["outlet"]))
        apc.power("10.10.50.205", "apc", "apc", host["outlet"], apc.IMMEDIATE_ON)
        time.sleep(5)

    applog.info("On cycle complete, waiting {} seconds for boot up".format(delay))
    time.sleep(delay)

    enabled_hosts = dict()
    for count in range(attempts):
        for key, host in hosts.items():
            if key not in enabled_hosts.keys():
                applog.info("Web UI check #{} for {}".format(count, host["fqdn"]))
                wm = WebManager(host["fqdn"])
                if wm.isWebUp() == True:
                    applog.info("Web UI is RUNNING for {}, delaying to give time to complete initialisation".format(host["fqdn"]))
                    time.sleep(delay)
                    applog.info("Exiting maintenance mode for {}".format(host["fqdn"]))
                    res = requests.post("https://awx.prjx.uk/api/v2/job_templates/10/launch/", verify=False, auth=HTTPBasicAuth('admin', 'bXlzdXBlcmxvbmdwYXNzd29yZAo='))
                    enabled_hosts[key] = True
                else:
                    applog.info("Web UI is DOWN for {}, delaying {} seconds before next check!".format(host["fqdn"], delay))
            else:
                applog.info("Host {}, has already completed, ignoring".format(host["fqdn"]))

        if len(enabled_hosts) >= len(hosts):
            applog.info("****** All Hosts sorted")
            break

        time.sleep(delay)


if __name__ == '__main__':
    main(False, hosts)
    os.sys.exit()