import click
from lib.vmware import *
from lib.apc import *
from lib.web import *
from prjxcore.ConfigManager import ConfigManager
from pprint import pprint

class VMWareRunner:
    hostmgr = None
    taskmgr = ESXiTaskManager()

    def __init__(self, vcenter, hosts):
        self.connect(vcenter['server'], vcenter['username'], vcenter['password'], vcenter['port'], hosts)

    def connect_other(self, vcenter, hosts):
        self.connect(vcenter['server'], vcenter['username'], vcenter['password'], vcenter['port'], hosts)

    def connect(self, server, username, password, port, hosts):
        conn_manager = ESXiConnectionManager(server, username, password, port)
        content = conn_manager.get_content()
        self.taskmgr = ESXiTaskManager()
        self.hostmgr = ESXiHostManager()
        self.hostmgr.get_hosts(content, esxi_hosts=hosts)
        # task_list = host_manager.enter_maintenance(60, True)

    def shutdown(self, force_shutdown = False):
        task_list = self.hostmgr.shutdown_hosts(force_shutdown)
        self.taskmgr.add_task_list(task_list)

    def maintenance(self, enabled = True):
        if enabled==True:
            task_list = self.hostmgr.enter_maintenance(60, True)
        else:
            task_list = self.hostmgr.exit_maintenance()

        self.taskmgr.add_task_list(task_list)

    def check_maintenance_status(self, expected_status):
        return self.hostmgr.check_maintenance_status(expected_status)



class APCRunner:
    apcmgr = None

    def connect(self, server, username, password, outlets):
        self.apcmgr = APCManager(server, username, password, outlets)

    def shutdown(self):
        self.apcmgr.power(self.apcmgr.IMMEDIATE_OFF)

    def up(self):
        self.apcmgr.power(self.apcmgr.IMMEDIATE_ON)


def __get_apc_runner(hosts = False):
    applog.debug("Getting APC runner")
    config = ConfigManager.get_section('apc')
    if not hosts:
        hosts = ConfigManager.get_section('hosts')

    outlets=[]
    for key, host in hosts.items(): outlets.append(host['outlet'])
    runner = APCRunner()
    runner.connect(config["server"], config["username"], config["password"], outlets)
    return runner


@click.group('host')
def host():
    """Commands for ESXi maintenance management"""


@host.command('pause')
def pause():
    # """ Put hosts into maintenance mode """
    applog.info("Paused - Enabling maintenance")
    runner = VMWareRunner(ConfigManager.get_section('vcenter'),
                        list(ConfigManager.get_section('hosts').keys()))

    runner.maintenance(True)
    runner.taskmgr.wait(True)


@host.command('unpause')
def unpause():
    """ Exit hosts from maintenance mode """
    applog.info("Unpaused - Exiting maintenance")
    runner = VMWareRunner(ConfigManager.get_section('vcenter'),
                        list(ConfigManager.get_section('hosts').keys()))
    runner.maintenance(False)
    runner.taskmgr.wait(True)


@host.command('shutdown')
def shutdown():
    """ Exit hosts from maintenance mode """
    applog.info("Shutdown - Evacuating hosts of VMs and shutting down")
    runner = VMWareRunner(ConfigManager.get_section('vcenter'),
                        list(ConfigManager.get_section('hosts').keys()))

    runner.maintenance(True)
    runner.taskmgr.wait(True)
    result = runner.check_maintenance_status(expected_status=True)

    if result!=False:
        applog.error("Shutdown aborting, {} is not in maintenance mode".format(result))
        raise Exception("Shutdown aborting, {} is not in maintenance mode".format(result))
    else:
        applog.info("All host successfully placed into maintenance mode, shutting them down")
        runner.shutdown(True)
        runner.taskmgr.wait(True)


@host.command('up')
def up():
    ## TODO: Implement checking if host is already powered on, also check if maintenance mode exit was successful...
    webui_sleep = ConfigManager.get_value("settings", "webui_check_sleep")
    power_sleep = ConfigManager.get_value("settings", "power_cycle_sleep")
    all_hosts = ConfigManager.get_section('hosts')
    cycle_hosts = {}

    for key, host in all_hosts.items():
        web = WebManager(key, host["web_ui"])
        if web.is_server_up():
            applog.info("{} is already UP, no need to power cycle".format(key))
        else:
            cycle_hosts[key] = host
            applog.info("{} is DOWN, it will be power cycled".format(key))

    if(len(cycle_hosts) > 0):
        applog.info("Powering Up")
        apc_runner = __get_apc_runner(cycle_hosts)
        applog.info("Power off outlets (Note bios MUST BE configured to switched on when power restored)")
        apc_runner.shutdown()

        applog.info("Off cycle complete, waiting {} seconds before powering On".format(power_sleep))
        time.sleep(power_sleep)

        applog.info("Powering up outlets outlets")
        apc_runner.up()
        applog.info("Power cycle processing complete... waiting {} seconds before exiting maintenance".format(webui_sleep))
        time.sleep(webui_sleep)
    else:
        applog.info("No hosts to power cycle, everything is already up!")

    vm_runner = VMWareRunner(ConfigManager.get_section('vcenter'),
                        list(ConfigManager.get_section('hosts').keys()))

    vm_runner.maintenance(False)
    vm_runner.taskmgr.wait(True)
    applog.info("Successfully exited maintenance mode")


if __name__ == '__main__':
    print("Cannot run this file directly")