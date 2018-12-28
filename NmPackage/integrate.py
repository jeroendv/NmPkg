from NmPackage import *
import argparse

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
                        help="Do not perform any actions, only simulate them.")

    args = parser.parse_args()

    # register custom exception handler
    h = MsBuildExceptionHandle(args.debug)
    sys.excepthook = h.exception_handler
    
    if args.debug:
        DebugLog.enabled = True
    
    with DebugLogScopedPush("cli arguments:"):
        DebugLog.print(str(args))
    
    return args

def main():

    args = parse_cli_args()
  
    with DebugLog.scopedPush("Integrate conanwith MsBuild *.vcxproj file"):
        Integrate(args.path)
        






