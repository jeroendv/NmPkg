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
        description="install a new packge")

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

    # install each packages
    for p in packages:
        install_package(p.qualifiedId)


def install_package(nmPackageId: NmPackageId):
    """
    download and install an NmPackage to the system-wide package dir
    """

    NmPackageDir = Path(os.environ['NmPackageDir'])
    DebugLog.print(NmPackageDir)


class NmPackage(object):
    """
    A concrete Nikon Metrology package.

    Unlike `NmPackageId` this class represent the actual set of files that make up the package.
    As such this class will perform disk IO to check files on disk and Network IO to fetch files from a server.
    """

    @property
    def nm_package_id(self) -> NmPackageId:
        return self._nm_package_id

    @property
    def package_dir(self) -> Path:
        """
        return the path of the package relative the package cache dir
        """
        return Path(self._nm_package_id.packageId) / Path(self.nm_package_id.versionId)

    @property
    def package_cache_dir(self) -> Path:
        """absolute `Path` to the package cache root directory"""
        return Path(os.environ['NmPackageDir'])

    
    def _get_git_project_slug(self) -> str:
        """
        create a git project slug for this package form the qualified package id

        A gitlab project slug has the following constraints:
         * Path can contain only letters, digits, '_', '-' and '.'.
         * Cannot start with '-'
         * cannot end in '.git' or '.atom'
        """
        git_slug = self._nm_package_id.qualifiedId

        # sanitize illegal chars
        import re
        git_slug = re.sub(r'[^a-zA-Z0-9_\-.]', '_', git_slug)

        # sanitize illegal start char
        git_slug = re.sub(r'^-', "_", git_slug)

        # sanitize illegal ending
        git_slug = re.sub(r'\.git$', "_git", git_slug)
        git_slug = re.sub(r'\.atom$', "_atom", git_slug)

        return git_slug

    def _get_git_repo_url(self) -> str:
        """url to the git repo of this package."""

        return "git@git@PC-CI-2.mtrs.intl:nmpackages/" + self._get_git_project_slug()
    

    def __init__(self, nm_package_id: NmPackageId):
        self._nm_package_id = nm_package_id

    def is_installed(self) -> bool:
        """
        check if this package is locally installed on the system.

        note that an installed package may be outdated!
        """
        return (self.package_cache_dir / self.package_cache_dir).is_dir()

    def is_outdated(self) -> bool:
        """
        check if a locally installed package is outdated.
        i.e. an outdated package will incurr network IO when being installed because.

        Note: non-installed packages are always considered outdated
        """
        pass

    def install(self):
        """
        install/update this package to the system wide package cache.

        Installing may incur network and disk IO.

        Throws in case of failure: e.g network disconnections, disk is full, etc
        """
        pass

    def uninstall(self):
        """
        Delete this package from the system wide package cache.

        Uninstall will perform Disk IO to remove the files from disk.
        """
        pass
