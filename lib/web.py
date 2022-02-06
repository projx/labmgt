import time
import urllib3
import requests
from prjxcore.AppLog import applog
from pprint import pprint

class WebManager:
    host = ""
    url = ""
    def __init__(self, host, url):
        self.set_url(host, url)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def set_url(self, host, url):
        self.host = host
        self.url = url

    def is_server_up(self):
        try:
            result = requests.head(self.url, verify=False, timeout=5)
            applog.debug("Check {}".format(self.url))
            pprint(result.status_code)
            if result.status_code == 200:
                return True
            return False
        except requests.ConnectionError as e:
            applog.debug("{} is not responding".format(self.url))
            return False

    def wait_for_server(self, delay, attempts):
        result = None
        for count in range(attempts):
            try:
                print("************************************")
                print(self.url)
                result = requests.head(self.url, verify=False, timeout=5)

                ## If we get a valid response... great
                if result.status_code == 200:
                    applog.info("{} is accessible, on attempt {}, total delay was {} seconds".format(self.url, count+1, count*delay))
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