
from conan_vs_integration import *
import argparse

"""veriry a conan integration with an MSBuild project
"""


def parse_cli_args():
    """parse the script input arguments"""
    parser = argparse.ArgumentParser(description = "Cveriry a conan integration with an MSBuild project")

    parser.add_argument("-v", "--verbose",
                    help="increase output verbosity",
                    action="store_true")

    parser.add_argument("-d","--debug",
                    help="enable debug output",
                    action="store_true")

    parser.add_argument("-N", "--dry-run",
                        help="Do not perform any actions, only simulate them.")

    args = parser.parse_args()
    if(args.debug):
        print("cli arguments: " + str(args)) 


    # don't show error trace in non-debug mode
    if(args.debug is False):
        sys.excepthook = exception_handler
    
    if args.debug:
        DebugLog.enabled = True
    
    return args


def main():
    args = parse_cli_args()

    vsProject = VsProject(os.getcwd())
    
    msg = VerifyIntegration(vsProject).verify()
    if(msg is not None):
        MsBuild.Error(msg)
        sys.exit(1)
    else:
        # everything verified correctly, return with a zero exit code to indicate success
        sys.exit(0)




def exception_handler(exception_type, exception, traceback):
    # All your trace are belong to us!
    # your format
    print(str(exception_type.__name__) + " : " + str(exception))




