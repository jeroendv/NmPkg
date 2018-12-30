from NmPackage import *
import argparse
from NmPackage.debug import *
from NmPackage.save import *
import sys

"""integrate NmPakakges into MSBuild for a given project
"""


def parse_cli_args():
    """parse the script input arguments"""
    parser = argparse.ArgumentParser(description = "Conan integration for Visual studio MSBuild")
                   
    parser.add_argument("-v", "--verbose",
                    help="increase output verbosity",
                    action="store_true")

    parser.add_argument("-d", "--debug",
                    help="enable debug output",
                    action="store_true")

    parser.add_argument("path",
                    help="path to the folder containing a single *.vcxproj file or a specific *.vcxproj file",
                    nargs='?',
                    default="./")

    parser.add_argument("-N", "--dry-run",
                        help="Do not perform any actions, only simulate them.",
                        action="store_true")

    args = parser.parse_args()

    with DebugLogScopedPush("cli arguments:"):
        DebugLog.print(str(args))

    return args

def main():
    # register custom exception handler
    sys.excepthook = exception_handler

    # parse cli input  
    args = parse_cli_args()

    # set debug log state
    DebugLog.enabled = args.debug
    
    # call 
    Integrate(Path(args.path))
        






