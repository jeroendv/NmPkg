"""
Main module of the NmPkg tool

This module defines the classes to describe projects, packages and project-package dependencies.

None of the classes in this module interact with the file system!
Instead they allow the dev to model a project and its package dependencies.

See the NmPackage.read module to create a `VsProject` obj by reading
'<projectName>.vxcproj' and '<projectName>.NmPackageDeps.props'

And the NmPackage.save module to save a 'VsProject' to disk thus modifying
'<projectName>.vxcproj' and '<projectName>.NmPackageDeps.props'

"""
from pathlib import PurePath
from NmPackage.debug import DebugLog
from pathlib import Path
import os


class VsProject:
    """
    Representation of a a Visual Studio project and its package dependencies

    identified by:
      * a *.vcxproj file
      * and a set of `NmPackageId`'s
    """

    def __init__(self, vcxproj_file: PurePath):
        self._vcxproj_file = PurePath(vcxproj_file)
        self._NmPackageSet = set()

    @property
    def dependencies(self) -> set:
        """The set of `NmPacakgeId` dependencies of this project"""
        return self._NmPackageSet

    @property
    def project_filepath(self) -> PurePath:
        """the *.vcxproj file path"""
        return self._vcxproj_file

    @property
    def projectName(self) -> str:
        """project name is the project file name without extension"""
        return self._vcxproj_file.stem

    def get_dependencies(self) -> set:
        return self._NmPackageSet


class NmPackageId(object):
    """
    A Nikon Metrology Package Identifier (NmPackage for short) is identified by <packageId> and a <versionId>
    """

    def __init__(self, packageId: str, versionId: str):
        self._packageId = packageId
        self._versionId = versionId

    @staticmethod
    def from_qualifiedId(qualifiedId: str):
        parts = qualifiedId.split("/")
        if len(parts) != 2:
            raise Exception("Invalid qualified package id: " + qualifiedId)

        return NmPackageId(parts[0], parts[1])

    @property
    def packageId(self) -> str:
        return self._packageId

    @property
    def versionId(self) -> str:
        return self._versionId

    @property
    def qualifiedId(self) -> str:
        return self.packageId + "/" + self.versionId

    def __repr__(self) -> str:
        return 'NmPackageId("{}", "{}")'.format(self.packageId, self.versionId)

    def __eq__(self, other) -> bool:
        return self.packageId == other.packageId and \
            self.versionId == other.versionId

    def __hash__(self):
        return hash(self.qualifiedId)


class NmPackageManager(object):
    """
    Manage NmPackages on the local system: Install, update and remove packages.
    
    This class will perform disk IO to check files on disk and Network IO to fetch files from a server.
    """
    @staticmethod
    def get_package_dir( nm_package_id: NmPackageId) -> Path:
        """
        return the path of the package in the system-wide package cache
        """
        return Path(nm_package_id.packageId) / Path(nm_package_id.versionId)

    @property
    def package_cache_dir(self) -> Path:
        """absolute `Path` to the system-wide package cache root directory"""
        return Path(os.environ['NmPackageDir'])

    @staticmethod
    def get_git_project_slug( nm_package_id: NmPackageId) -> str:
        """
        create a git project slug for this package from the qualified package id

        A gitlab project slug has the following constraints:
         * Path can contain only letters, digits, '_', '-' and '.'.
         * Cannot start with '-'
         * cannot end in '.git' or '.atom'
        """
        git_slug = nm_package_id.qualifiedId

        # sanitize illegal chars
        import re
        git_slug = re.sub(r'[^a-zA-Z0-9_\-.]', '_', git_slug)

        # sanitize illegal start char
        git_slug = re.sub(r'^-', "_", git_slug)

        # sanitize illegal ending
        git_slug = re.sub(r'\.git$', "_git", git_slug)
        git_slug = re.sub(r'\.atom$', "_atom", git_slug)

        return git_slug

    @staticmethod
    def get_git_repo_url(nm_package_id: NmPackageId) -> str:
        """url to the git repo of a package."""
        slug = NmPackageManager.get_git_project_slug(nm_package_id)
        return "git@PC-CI-2.mtrs.intl:nmpackages/{}.git".format(slug)


    @staticmethod
    def is_installed( nm_package_id: NmPackageId) -> bool:
        """
        check if a package is locally installed on the system.

        note that an installed package may be outdated!
        """
        return (self.package_cache_dir / self.package_cache_dir).is_dir()

    @staticmethod
    def is_outdated( nm_package_id: NmPackageId) -> bool:
        """
        check if a locally installed package is outdated.
        i.e. an outdated package will incurr network IO when being installed because.

        Note: non-installed packages are always considered outdated
        """
        pass

    @staticmethod
    def install( nm_package_id: NmPackageId):
        """
        install/update a package to the system wide package cache.

        Installing may incur network and disk IO.

        Throws in case of failure: e.g network disconnections, disk is full, etc
        """
        pass

    @staticmethod
    def uninstall( nm_package_id: NmPackageId):
        """
        Delete a package from the system wide package cache.

        Uninstall will perform Disk IO to remove the files from disk.
        """
        pass
