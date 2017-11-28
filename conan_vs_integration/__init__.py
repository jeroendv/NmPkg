
import os
import sys
from pathlib import Path
import hashlib
import binascii
import shutil
import traceback


import xml.etree.ElementTree as ET


class MsBuild:
    
    def Error(msg):
        """print an MSBuild error message to stderr"""
        sys.stderr.write("Error: " + msg + "\n")

class MsBuildExceptionHandle:
    """Exception handler for processing by MsBuild"""

    def __init__(self, debug):
        self.debug = debug

    def exception_handler(self, exception_type, exception, tb):
        # format python exception as MsBuild error messages
        MsBuild.Error(str(exception_type.__name__) + " : " + str(exception))
        if (self.debug):
            traceback.print_tb(tb)


class DebugLogScopedPush:
    def __init__(self, msg = None):
        self.msg = msg

    def __enter__(self):
        if(self.msg is not None):
            DebugLog.print(self.msg)
            
        self.originalIndentLvl = DebugLog.indentLvl
        DebugLog.push()
    
    def __exit__(self, type, value, traceback):
        DebugLog.pop()
        assert(DebugLog.indentLvl == self.originalIndentLvl)


class DebugLog:
    """An indentation aware debug log stream"""

    indentLvl = 0
    enabled = False

    def print(msg):
        # skip debug messages if debug mode is not enabled!
        if (not DebugLog.enabled):
            return 

        print("|  "*DebugLog.indentLvl + msg)

    def push():
        DebugLog.indentLvl += 1
        return DebugLog.indentLvl

    def scopedPush(msg = None):
        return DebugLogScopedPush(msg)

    def pop():
        newIndentLvl = DebugLog.indentLvl - 1
        # indentLvl can't become negative
        if newIndentLvl < 0:
            newIndentLvl = 0
        
        DebugLog.indentLvl = newIndentLvl
        return DebugLog.indentLvl



class VsProject:
    """A Visual Studio project consists of a folder and a single *.vcxproj file
    """
    def __init__(self, path):
        self._path = Path(path)
        self._verify_path()

    def _verify_path(self):
        if (not self._path.is_dir()):
            raise Exception("'%s' is not an existing directory" % self._path.absolute())

        # verify that the folder contains only one project
        projects = [x for x in self._path.iterdir() if x.is_file() and x.suffix == '.vcxproj']
        if (len(projects) == 0):
            raise Exception("'%s' is not an a project folde, no '*.vcxproj' file is present" % self._path.absolute())
        elif (len(projects) > 1):
            raise Exception("'%s' contains multiple '*.vcxproj' project files" % self._path.absolute())
        else:
            assert(len(projects) == 1)
            self._projectFile = projects[0]
            

    def path(self):
        """return pathlib.Path for the project folder"""
        return self._path

    def projectFile(self):
        """return pathlib.Path for the project file"""        
        return self._projectFile

class VsConanProject(VsProject):
    """A Visual Studio project with conan integration

    it consists of a folder containing:
     * a single *.vcxproj file
     * a conanfile.txt file
     * a Conan.targets file
    """
    def __init__(self, path):
        VsProject.__init__(self, path)

    def _verify_path(self):
        VsProject._verify_path(self)
        
        # verify that a 'conanfile.txt' is present
        conanFile = self._path / Path("conanfile.txt")
        if ( not conanFile.exists()):
            raise Exception(str(conanFile.absolute()) + " is missing!")
        
        # verify that a 'Conan.targets' is present
        f = self._path  / Path('Conan.targets')
        if (not f.exists()):
            raise Exception(str(f.absolute()) + " is missing!")
            




class VerifyIntegration:

    def __init__(self, vsConanProject):
        self.vsConanProject = vsConanProject
        self.messages = []

    def verify(self):
        """verify an integration
        returns a failure message or None if all is ok
        """
        assert(self.vsConanProject.path().samefile(os.getcwd()))

        packageDir = Path(__file__).parent

        if (not os.path.isfile("Conan.targets")):
            return r"""No 'Conan.Targets' file found.
            Use the 'integrate' command to generate the file."""

        return self._verifyFileChecksum("Conan.targets")



    def _verifyFileChecksum(self, file):
        """verify a file checksum
        returns a failure message or None if all is ok
        """
        packageDir = Path(__file__).parent
        refFile = packageDir / file
        userFile = Path(os.getcwd()) / file

        # both the reference and the user file should exists
        assert(os.path.isfile(refFile))
        assert(os.path.isfile(userFile))

        with DebugLog.scopedPush("checking hash for file '%s'" % file):
            refFileDigest = filehash(refFile)
            userFileDigest = filehash(userFile)

            if refFileDigest != userFileDigest:
                DebugLog.print("hash mismatch!")
                DebugLog.print("referenceFile: " + binascii.hexlify(refFileDigest).decode('ascii'))
                DebugLog.print("userFile     : " + binascii.hexlify(userFileDigest).decode('ascii'))
                
                return """{file} has been illegally modified.
                The Conan.Targets file is an auto generated file from the 'integrate' command. It may not be modified.
                Use the 'integrate -u' command to regenerate the file.""".format(
                    file = file
                )
            else:
                DebugLog.print("hash match! => file is up to date")
                return None


from xml.dom import minidom
def Integrate(vsProject):
    """Intergrate conan with an Msbuild Project

    create conanfile.txt & Conan.targets
    integrate into *.vcxproj file
    """
    assert(Path(vsProject.path()).is_dir())
    assert(Path(os.getcwd()).samefile(vsProject.path()))
    
    packageDir = Path(__file__).parent

    # copy the Conan.targets
    refFile = packageDir / "conanfile.txt"
    shutil.copy(refFile, vsProject.path())

    # copy the Conan.targets
    refFile = packageDir / "Conan.targets"
    shutil.copy(refFile, vsProject.path())
    
    # read the project xml file
    projDom = minidom.parse(str(vsProject.projectFile()))

    # integrate the Conan.targes file into the project
    # i.e. add 
    #       <Import Project="Conan.targets" />
    # to the project file
    import_node = projDom.createElement("Import")
    import_node.setAttribute("Project", "Conan.targets")


    proj_node = projDom.getElementsByTagName("Project")
    assert len(proj_node) == 1
    proj_node = proj_node[0]
    proj_node.appendChild(import_node)



    # include the conconfile.txt in the projec file
    # i.e. add
    #       <ItemGroup>
    #         <Text Include="conanfile.txt" />
    #       </ItemGroup>
    # to the project file
    text_node = projDom.createElement("Text")
    text_node.setAttribute("Include", "conanfile.txt")

    itemgroup_node = projDom.createElement("ItemGroup")
    itemgroup_node.appendChild(text_node)
    

    proj_node = projDom.getElementsByTagName("Project")
    assert len(proj_node) == 1
    proj_node = proj_node[0]
    proj_node.appendChild(itemgroup_node)

    # write the updated project xml config to file
    with open(vsProject.projectFile(), 'tw') as f:
        f.write(projDom.toprettyxml())









def UpdateIntegration(vsConanProject):
    assert(vsConanProject.path().samefile(os.getcwd()))

    packageDir = Path(__file__).parent
    refFile = packageDir / "Conan.targets"
    shutil.copy(refFile, vsConanProject.path())

    refFile = packageDir / "ConanVsIntegration.Debug.targets"
    shutil.copy(refFile, vsConanProject.path())

def filehash(file):
    """compute file checksum"""
    h = hashlib.sha256()
    with open(file, 'rb') as f:
        h.update(f.read())
        return h.digest()



