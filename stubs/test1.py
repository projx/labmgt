## https://programtalk.com/python-examples/pyVmomi.vim.host.MaintenanceSpec/
## https://github.com/vmware/pyvmomi-community-samples/issues/274
## https://tanulb.medium.com/ansible-in-a-virtual-environment-c3ae234f7629

from pyVim import connect, task
from pyVmomi import vim
from tools import cli
from tools import tasks
from pprint import pprint
import getpass
import ssl
import requests
import atexit

host = "10.10.50.69"
user = "administrator@vsphere.local"
password = "J4=866Tyewr8H43J"
port = "443"
server_instance = False
cluster_name = "Home"
host_name = "esx-04.prjx.uk"

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
                logger.info(task.info)
        else:
            logger.info("No tasks..")

    def _progress_output(self, task, progress):
        if progress is None:
            return
        try:
            progess = str(progress)

            if "error" in progress:
                return  ## Just return at this point.. the exception handler in waitX() will deal with this

            if progress.isdigit():
                progress = progress + "%"

            logger.info("{} on {}, progress is {}".format(task.info.descriptionId, task.info.entityName, progress))
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
                logger.info("Houston, we have a problem: " + e.msg)

def get_obj(content, vimtype, name = None):
    return [item for item in content.viewManager.CreateContainerView(
        content.rootFolder, [vimtype], recursive=True).view]

requests.packages.urllib3.disable_warnings()
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
context.verify_mode = ssl.CERT_NONE

# connect this thing
server_instance = connect.SmartConnectNoSSL(host=host, user=user, pwd=password, port=port)
atexit.register(connect.Disconnect, server_instance)

content = server_instance.RetrieveContent()
for cluster_obj in get_obj(content, vim.ComputeResource):
    print(cluster_obj.name)
    for host in cluster_obj.host:
        print(host.name)

        if host.name == host_name:
            print("Found")
            host.
    # else:
    #     print
    #     cluster_obj.name