
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

    vsProject = VsProject(os.getcwd())
    
    msg = VerifyIntegration(vsProject).verify()
    if(msg is not None):
        MsBuild.Error(msg)
        sys.exit(1)
    else:
        # everything verified correctly, return with a zero exit code to indicate success
        sys.exit(0)





