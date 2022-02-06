import click
from lib.vmware import *
from prjxcore.ConfigManager import ConfigManager
from pprint import pprint

class VMWareRunner:
    hostmgr = None
    taskmgr = ESXiTaskManager()

    def connect(self, server, username, password, port, hosts):
        conn_manager = ESXiConnectionManager(server, username, password, port)
        content = conn_manager.get_content()
        taskmgr = ESXiTaskManager()
        self.hostmgr = ESXiHostManager()
        self.hostmgr.get_hosts(content, esxi_hosts=hosts)
        # task_list = host_manager.enter_maintenance(60, True)

    def shutdown(self, force_shutdown = False):
        task_list = self.hostmgr.shutdown_hosts(60, force_shutdown)
        self.taskmgr.add_task_list(task_list)

    def maintenance(self, enabled = True):
        if enabled==True:
            task_list = self.hostmgr.enter_maintenance(60, True)
        else:
            task_list = self.hostmgr.exit_maintenance()

        self.taskmgr.add_task_list(task_list)





def get_runner():
    applog.info("Getting runner")
    vcenter = ConfigManager.get_section('vcenter')
    hosts = ConfigManager.get_section('hosts')
    hosts = list(hosts.keys())
    runner = VMWareRunner()
    runner.connect(vcenter['server'], vcenter['username'], vcenter['password'], vcenter['port'], hosts)
    return runner


@click.group('maintenance')
def maintenance():
    """Commands for ESXi maintenance mananegement"""


@maintenance.command('enable')
def enable():
    """ Put hosts into maintenance mode """
    applog.info("Enabling maintenance")
    runner = get_runner()
    runner.maintenance(True)
    runner.taskmgr.wait(True)


@maintenance.command('disable')
def disable():
    """ Exit hosts from maintenance mode """
    applog.info("Exiting maintenance")
    runner = get_runner()
    runner.maintenance(False)
    runner.taskmgr.wait(True)

if __name__ == '__main__':
    print("Cannot run this file directly")