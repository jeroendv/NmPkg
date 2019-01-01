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
    def project_filepath(self) -> PurePath:
        """the *.vcxproj file path """
        return self._vcxproj_file

    @property
    def projectName(self) -> str:
        """project name is the project file name without extension"""
        return self._vcxproj_file.stem


class NmPackageId(object):
    """
    A Nikon Metrology Package Identifier (NmPackage for short) is identified by <packageId> and a <versionId>
    """

    def __init__(self, packageId: str, versionId: str):
        self._packageId = packageId
        self._versionId = versionId

    @property
    def packageId(self) -> str:
        return self._packageId

    @property
    def versionId(self) -> str:
        return self._versionId

    @property
    def qualifiedId(self) -> str:
        return self.packageId + "\\" + self.versionId

    def __repr__(self) -> str:
        return 'NmPackageId("{}", "{}")'.format(self.packageId, self.versionId)

    def __eq__(self, other) -> bool:
        return self.packageId == other.packageId and \
            self.versionId == other.versionId

    def __hash__(self):
        return hash(self.qualifiedId)
