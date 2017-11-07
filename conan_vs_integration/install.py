from conan_vs_integration import *
import argparse
import subprocess


""" install conan dependencies for a given project
"""


def parse_cli_args():
    """parse the script input arguments"""
    parser = argparse.ArgumentParser(description="install conan dependencies for a given project")

    parser.add_argument("-v", "--verbose",
                    help="increase output verbosity",
                    action="store_true")

    parser.add_argument("-d", "--debug",
                    help="enable debug output",
                    action="store_true")
                   

    parser.add_argument("-N", "--dry-run",
                        help="Do not perform any actions, only simulate them.")
    
    parser.add_argument("--Platform")
    parser.add_argument("--Toolset")
    parser.add_argument("--Configuration")
    parser.add_argument("--VisualStudioVersion")

    args = parser.parse_args()

    if args.debug:
        DebugLog.enabled = True

    with DebugLogScopedPush("cli arguments:"):
        DebugLog.print(str(args))

    #don't show error trace in non-debug mode
    if (not args.debug):
        sys.excepthook = exception_handler
    
    return args

def main():
    args = parse_cli_args()

    cmd = ['conan', 'install', './']
    cmd += ['-s', processPlatform(args)]
    cmd += ['-s', processConfiguration(args)]
    cmd += ['-s', processVisualStudioVersion(args)]
    
    if (args.debug):
        print(" ".join(cmd))

    subprocess.check_call(cmd)


def processPlatform(args):
    if (args.Platform == "Win32"):
        return "arch=x86"
    elif(args.Platform == "x64"):
        return "arch=x86_64"
    else:
        raise Exception("unknown platform '%s', it can not be mapped to a conan.arch setting" % args.Platform)

def processVisualStudioVersion(args):
    if(args.VisualStudioVersion == "11.0"):
        return "compiler.version=11"
    
    raise Exception("unknown VisualStudioVersion '%s', it can not be mapped to a conan.compiler.version setting" % args.VisualStudioVersion)
    


def processConfiguration(args):
    return "build_type=" + args.Configuration




def exception_handler(exception_type, exception, traceback):
    # All your trace are belong to us!
    # your format
    print(str(exception_type.__name__) + " : " + str(exception))


