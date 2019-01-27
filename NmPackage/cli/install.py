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
        description="install a new package")

    parser.add_argument("-v", "--verbose",
                        help="increase output verbosity",
                        action="store_true")

    parser.add_argument("-d", "--debug",
                        help="enable debug output",
                        action="store_true")

    parser.add_argument("qualifiedPackageId",
                        help="qualifiedId of the package to be added",
                        nargs="?")

    parser.add_argument("--vcxproj",
                        help="path to the folder containing a single *.vcxproj file or a specific *.vcxproj file")

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

    # collect all packages to be installed
    packages = set()
    if args.qualifiedPackageId is not None:
        packages.add(NmPackageId.from_qualifiedId(args.qualifiedPackageId))

    if args.vcxproj is not None:
        try:
            vcxproj_file = find_vcxproj(Path(args.vcxproj))
        except Exception as e:
            # no project found!
            pass

        vsProject = VsProjectFiler().deserialize(vcxproj_file)
        packages.update(vsProject.dependencies)

    with DebugLogScopedPush("found packages:"):
        for p in packages:
            DebugLog.print(p.qualifiedId)

    # install all of the packages
    mgr = NmPackageManager.get_system_manager()
    for p in packages:
        mgr.install(p)
