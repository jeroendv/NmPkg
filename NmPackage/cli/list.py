from NmPackage import *
import argparse
from NmPackage.debug import *
from NmPackage.save import *
from NmPackage import *
from pathlib import Path
import os


def parse_cli_args():
    """parse the script input arguments"""
    parser = argparse.ArgumentParser(
        description="list all installed packages")

    parser.add_argument("-v", "--verbose",
                        help="increase output verbosity",
                        action="store_true")

    parser.add_argument("-d", "--debug",
                        help="enable debug output",
                        action="store_true")

    parser.add_argument("-N", "--dry-run",
                        help="Do not perform any actions, only simulate them.",
                        action="store_true")

    args = parser.parse_args()

    # set debug log state
    DebugLog.enabled = args.debug

    with DebugLogScopedPush("cli arguments:"):
        DebugLog.print(str(args))

    return args


def main():
    # register custom exception handler
    sys.excepthook = exception_handler

    # parse cli input
    args = parse_cli_args()

    list_installed_packages()

def list_installed_packages():
    mgr = NmPackageManager.get_system_manager()
    
    for p in sorted(mgr.get_installed_packages(), key=lambda nmPackageId: nmPackageId.qualifiedId ):
        print(p.qualifiedId)

   
        



