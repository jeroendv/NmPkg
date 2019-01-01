from NmPackage import *
import argparse
from NmPackage.debug import *
from NmPackage.save import *
from NmPackage import *
from pathlib import Path


def parse_cli_args():
    """parse the script input arguments"""
    parser = argparse.ArgumentParser(
        description="add a new NmPackage dependency to a project")

    parser.add_argument("-v", "--verbose",
                        help="increase output verbosity",
                        action="store_true")

    parser.add_argument("-d", "--debug",
                        help="enable debug output",
                        action="store_true")

    parser.add_argument("qualifiedPackageId",
                        help="qualifiedId of the package to be added",
                        nargs=1)

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
    add_package(Path(args.path), NmPackageId.from_qualifiedId(args.qualifiedPackageId[0]))


def add_package(path: Path, nmPackageId: NmPackageId):
    """
    Add a `NmPackageId` dependency to a project
    """
    vcxproj_filepath = find_vcxproj(Path(path))

    vsProject = VsProjectFiler().deserialize(vcxproj_filepath)

    vsProject.dependencies.add(nmPackageId)

    VsProjectFiler().serialize(vsProject)
