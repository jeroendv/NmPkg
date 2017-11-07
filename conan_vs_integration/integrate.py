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

    if (args.update):
        with DebugLog.scopedPush("integration update"):
            msg = VerifyIntegration(vsProject).verify()
            if (msg is None):
                DebugLog.print("everything verified ok, so exit with success-code")
                sys.exit(0)
            else:
                DebugLog.print("verification failed! => force reintegration")
                
                UpdateIntegration(vsProject)

                # force restart to pick up on new '*.targets' files
                MsBuild.Error("conan integration was updated. restart build is required!")
                sys.exit(1)
    

def exception_handler(exception_type, exception, traceback):
    # All your trace are belong to us!
    # your format
    print(str(exception_type.__name__) + " : " + str(exception))




