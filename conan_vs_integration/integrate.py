from conan_vs_integration import *
import argparse

"""integrate conan into MSBuild for a given project
"""


def parse_cli_args():
    """parse the script input arguments"""
    parser = argparse.ArgumentParser(description = "Conan integration for Visual studio MSBuild")

    parser.add_argument("-u", "--update",
                        help="verify the integration and reintegration in needed.",
                        action="store_true")
                        
    parser.add_argument("-v", "--verbose",
                    help="increase output verbosity",
                    action="store_true")

    parser.add_argument("-d", "--debug",
                    help="enable debug output",
                    action="store_true")
    parser.add_argument("path",
                    help="path to the folder containing a *.vcxproj file",
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


    if (args.update):
        with DebugLog.scopedPush("integration update"):
            vsConanProject = VsConanProject(args.path)
            msg = VerifyIntegration(vsConanProject).verify()
            if (msg is None):
                DebugLog.print("everything verified ok, so exit with success-code")
                sys.exit(0)
            else:
                DebugLog.print("verification failed! => force reintegration")
                
                UpdateIntegration(vsConanProject)

                # force restart to pick up on new '*.targets' files
                MsBuild.Error("conan integration was updated. restart build is required!")
                sys.exit(1)
    else:
        assert(args.update is False)
        with DebugLog.scopedPush("Integrate conanwith MsBuild *.vcxproj file"):
            vsProject = VsProject(args.path)
            Integrate(vsProject)




