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
import shutil


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
    def get_package_dir(nm_package_id: NmPackageId) -> Path:
        """
        return the path of the package in the system-wide package cache
        """
        return Path(nm_package_id.packageId) / Path(nm_package_id.versionId)

    @property
    def package_cache_dir(self) -> Path:
        """absolute `Path` to the system-wide package cache root directory"""
        return self._package_cache_dir

    def __init__(self, package_cache_dir: Path):
        self._package_cache_dir = package_cache_dir

    @staticmethod
    def get_system_manager():
        """
        Return the NmPackageManager to manage in the system-wide cache of the local machine.
        """
        system_wide_package_cache = Path(os.environ['NmPackageDir'])

        if not system_wide_package_cache.is_dir():
            raise Exception(
                "The system-wide package cache dir does not exists.")

        return NmPackageManager(system_wide_package_cache)

    @staticmethod
    def get_git_project_slug(nm_package_id: NmPackageId) -> str:
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

    def is_installed(self, nm_package_id: NmPackageId) -> bool:
        """
        check if a package is locally installed on the system.

        note that an installed package may be outdated!
        """
        return (self.package_cache_dir / NmPackageManager.get_package_dir(nm_package_id)).is_dir()

    def is_outdated(self, nm_package_id: NmPackageId) -> bool:
        """
        check if a locally installed package is outdated.
        i.e. an outdated package will incurr network IO when being installed because.

        Note: non-installed packages are always considered outdated
        """
        pass

    def install(self, nm_package_id: NmPackageId):
        """
        install/update a package to the system wide package cache.

        Installing may incur network and disk IO.

        Throws in case of failure: e.g network disconnections, disk is full, etc
        """
        pass

    def uninstall(self, nm_package_id: NmPackageId):
        """
        Delete a package from the system wide package cache.

        Uninstall will perform Disk IO to remove the files from disk.
        """
        if not self.is_installed(nm_package_id):
            # Nothing to do: the package is not installed
            return
        absolute_package_path = self.package_cache_dir / self.get_package_dir(nm_package_id)  
        delete_tree(absolute_package_path)

        if 0 == len(list(absolute_package_path.parent.iterdir())):
            # the last version of the package is removed, 
            # remove the package folder as well
            absolute_package_path.parent.rmdir()

    def get_installed_packages(self) -> set:
        """
        Return a set of NmPackageId's that are installed in the system-wide package cache
        """
        # the packege cache has fixes structure
        #    <packageId>/<versionId>
        # lets find all directories in the system-wide package cache that m
        all_package_folders = self.package_cache_dir.glob("*/*")
        packages = set()
        for p in all_package_folders:
            if not p.is_dir():
                # skip files
                # e.g. the system-wide packge cache folder, or the packageId folder may contain some readme files
                continue

            # plit the relative path in its two parts <packageId> & <versionId>
            rel_path = p.relative_to(self.package_cache_dir)
            path_parts = rel_path.parts
            assert 2 == len(path_parts)

            # aggregate
            packages.add(NmPackageId(path_parts[0], path_parts[1]))

        return packages


def delete_tree(path: Path):
    """
    Recursively delete a whole directory tree.

    Note that this method will even delete read-only files provided that the user has the rights.
    """
    if not path.exists():
        return

    if not path.is_dir():
        raise Exception("input `path` must be a directory.")

    def onerror(func, path, exc_info):
        """
        Error handler for ``shutil.rmtree``.

        If the error is due to an access error (read only file)
        it attempts to add write permission and then retries.

        If the error is for another reason it re-raises the error.

        Usage : ``shutil.rmtree(path, onerror=onerror)``
        """
        import stat
        if not os.access(path, os.W_OK):
            # Is the error an access error ?
            os.chmod(path, stat.S_IWUSR)
            func(path)
        else:
            raise

    import shutil
    shutil.rmtree(path, onerror=onerror)

