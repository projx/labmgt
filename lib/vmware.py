from pyvim import connect, task
from pyVmomi import vim
from pprint import pprint
from prjxcore.AppLog import applog

import atexit
import time
import requests
import urllib3
import ssl

"""
Consolidates "tasks" returned by calls to pymomi, then allows wait() for the tasks to be completed...
"""
class ESXiTaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def add_task_list(self, group):
        self.tasks = self.tasks + group

    def check(self):
        if len(self.tasks):
            for task in self.tasks:
                applog.info(task.info)
        else:
            applog.info("No tasks..")

    def _progress_output(self, task, progress):
        if progress is None:
            return
        try:
            progess = str(progress)

            if "error" in progress:
                return  ## Just return at this point.. the exception handler in waitX() will deal with this

            if progress.isdigit():
                progress = progress + "%"

            applog.info("{} on {}, progress is {}".format(task.info.descriptionId, task.info.entityName, progress))
        except (TypeError) as e:
            pass

    def clear(self):
        self.tasks = list()

    def wait(self, show_progress=False):
        if len(self.tasks) > 0:
            try:
                if show_progress:
                    progress_call = self._progress_output
                else:
                    progress_call = None

                task.WaitForTasks(tasks=self.tasks, onProgressUpdate=progress_call)
            except (Exception) as e:
                applog.info("Houston, we have a problem: " + e.msg)
                raise e


"""
Manages the connection to ESXi/vCenter hosts, including the accessing the server-instance and data contents
"""
class ESXiConnectionManager:
    def __init__(self, svr, usr, pss, prt):
        self.server_instance = None
        try:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            self.server_instance = connect.SmartConnectNoSSL(host=svr, user=usr, pwd=pss, port=prt)
            atexit.register(connect.Disconnect, self.server_instance)
            content = self.get_content()
        except IOError as ex:
            raise SystemExit("unable to connect to vCenter / ESXi host..")

    def get_server_instance(self):
        return self.server_instance

    def get_content(self):
        return self.server_instance.RetrieveContent()


"""
Incapsulate functions for identifying and managing the ESXi hosts
"""
class ESXiHostManager:
    def __init__(self):
        self.hosts = dict()



    def shutdown_hosts(self, forced_shutdown=False):
        tasks = list()
        for key, host in self.hosts.items():
            applog.info("Host {} is now being shutdown".format(key))
            task = host.ShutdownHost_Task(forced_shutdown)
            tasks.append(task)

        return tasks

    def power_on_hosts(self):
        tasks = list()
        for key, host in self.hosts.items():
            applog.info("Host {} is now being powered on".format(key))
            task = host.PowerOnHost_Task()
            tasks.append(task)

        return tasks

    def enter_maintenance(self, timeout=30, vacate=True):
        tasks = list()
        for key, host in self.hosts.items():
            applog.info("Host {} is entering maintenance mode".format(key))
            task = host.EnterMaintenanceMode_Task(timeout, vacate)
            tasks.append(task)

        return tasks

    def exit_maintenance(self, timeout=30):
        tasks = list()
        for key, host in self.hosts.items():
            applog.info("Host {} is exiting maintenance mode".format(key))
            task = host.ExitMaintenanceMode_Task(timeout)
            tasks.append(task)

        return tasks

    def get_hosts(self, content, esxi_hosts=[]):
        self.hosts = dict()
        host_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)

        ## Here we keep a class-local reference to the hosts, filtering for specific hosts if defined in "hostnames"
        for host in host_view.view:
            applog.info("Found host: {}".format(host.name))
            if len(esxi_hosts) == 0:
                self.hosts[host.name] = host
            else:
                for hostname in esxi_hosts:
                    if (host.name == hostname):
                        applog.info("matched host: {}".format(host.name))
                        self.hosts[host.name] = host

        return self.hosts



