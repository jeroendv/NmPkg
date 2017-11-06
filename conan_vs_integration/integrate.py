import sys
import argparse
import os
from pathlib import Path
import shutil


def parse_cli_args():
    """parse the script input arguments"""
    global args
    parser = argparse.ArgumentParser(description = "Conan integration for Visual studio MSBuild")

    parser.add_argument("-v", "--verbose",
                    help="increase output verbosity",
                    action="store_true")

    parser.add_argument("-d","--debug",
                    help="enable debug output",
                    action="store_true")

    parser.add_argument("-N", "--dry-run",
                        help="Do not perform any actions, only simulate them.")

    # parser.add_argument("command",
    #                     help="which command to invoke"
    #                     nargs="?")
    args = parser.parse_args()
    if(args.debug):
        print("cli arguments: " + str(args)) 


    # don't show error trace in non-debug mode
    if(args.debug is False):
        sys.excepthook = exception_handler

def main():
    parse_cli_args()
    print(args.verbose)
    packageDir = Path(__file__).parent
    shutil.copyfile(packageDir / "Conan.targets", Path(os.getcwd()) / "Conan.targets" )






def exception_handler(exception_type, exception, traceback):
    # All your trace are belong to us!
    # your format
    print(str(exception_type.__name__) + " : " + str(exception))




