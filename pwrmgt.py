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