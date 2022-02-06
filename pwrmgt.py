#!/usr/bin/env python3

from prjxcore.ConfigManager import ConfigManager
from prjxcore.AppLog import applog
from lib import host_args
from pprint import pprint
import click
import os

@click.group()
@click.option('-s', '--suppress', is_flag=True, default=False, help="Suppress most output (Note actual output level is defined in settings.yml")
def main(suppress):
    """ LAB POWER MANAGEMENT SYSTEM """
    # Handle flags
    show_output = False if suppress else True
    applog.setup(show_output, False)
    applog.set_enabled(True)
    applog.set_info(True)

    workdir = dir_path = os.path.dirname(os.path.realpath(__file__))
    cfg_path = workdir + "/etc/config.yml"
    ConfigManager.load(cfg_path)
    debug = ConfigManager.get_value("settings", "show_debug_output")
    applog.set_debug(debug)

if __name__ == '__main__':

    ## Register the CLI arguments - These are broken out to make them more modular
    main.add_command(host_args.host)
    main()



200
200
Traceback (most recent call last):
  File "/app/pwrmgt.py", line 30, in <module>
    main()
  File "/usr/local/lib/python3.10/site-packages/click/core.py", line 1128, in __call__
    return self.main(*args, **kwargs)
  File "/usr/local/lib/python3.10/site-packages/click/core.py", line 1053, in main
    rv = self.invoke(ctx)
  File "/usr/local/lib/python3.10/site-packages/click/core.py", line 1659, in invoke
    return _process_result(sub_ctx.command.invoke(sub_ctx))
  File "/usr/local/lib/python3.10/site-packages/click/core.py", line 1659, in invoke
    return _process_result(sub_ctx.command.invoke(sub_ctx))
  File "/usr/local/lib/python3.10/site-packages/click/core.py", line 1395, in invoke
    return ctx.invoke(self.callback, **ctx.params)
  File "/usr/local/lib/python3.10/site-packages/click/core.py", line 754, in invoke
    return __callback(*args, **kwargs)
  File "/app/lib/host_args.py", line 144, in up
    vm_runner.taskmgr.wait(True)
  File "/app/lib/vmware.py", line 62, in wait
    raise e
  File "/app/lib/vmware.py", line 59, in wait
    task.WaitForTasks(tasks=self.tasks, onProgressUpdate=progress_call)
  File "/usr/local/lib/python3.10/site-packages/pyVim/task.py", line 216, in WaitForTasks
    raise err
pyVmomi.VmomiSupport.vim.fault.InvalidState: (vim.fault.InvalidState) {
   dynamicType = <unset>,
   dynamicProperty = (vmodl.DynamicProperty) [],
   msg = 'The operation is not allowed in the current state.',
   faultCause = <unset>,
   faultMessage = (vmodl.LocalizableMessage) []
