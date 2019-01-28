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

    parser.add_argument("qualifiedPackageIds",
                        help="qualifiedId of the package to be added",
                        nargs="*")

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
    for id in args.qualifiedPackageIds:
        packages.add(NmPackageId.from_qualifiedId(id))

    # get system-wide package manager
    mgr = NmPackageManager.get_system_manager()

    # if dry-run then don't actually proceed to install all packages
    if args.dry_run:
        return

    # uninstall all of the packages
    for p in packages:
        DebugLog.print("uninstalling NmPackage: " + p.qualifiedId)
        mgr.uninstall(p)



   

def collect_all_packages(tree: Path) -> set:
    """ 
    recursively find all *.NmPackageDeps.props and collect all packages
    """
    packages = set()

    assert Path(tree).is_dir()

    # traverse the tree ignoring vcs folders
    ignoreFolders = ['.svn', '.git']
    for root, dirs, files in os.walk(tree):
        for f in ignoreFolders:
            if (f in dirs):
                dirs.remove(f) 

        # get list of all NmPackage listengs in 'root'
        nm_package_deps_files = [Path(root)/Path(f) for f in files if f.endswith(".NmPackageDeps.props")]

        # collect all the NmPackageId's
        for file in nm_package_deps_files:
            DebugLog.print("found: " + str(file))
            with file.open("tr") as f:
                packages.update(NmPackageDepsFileFormat.deserialize(f.read()))\
    
    return packages
        


   

