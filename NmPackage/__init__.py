
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
    """A Visual Studio project is identified by a *.vcxproj file
    """
    def __init__(self, vcxproj_file):
        self._vcxproj_file = Path(vcxproj_file)
        self._verify_path()

    def _verify_path(self):
        if (not self._vcxproj_file.is_file()):
            raise Exception("'%s' is not an existing file" % self._vcxproj_file.absolute())
        if not self._vcxproj_file.match("*.vcxproj"):
            raise Exception("")

    def path(self):
        """return pathlib.Path for the project folder"""
        return self._vcxproj_file.parent

    def projectFile(self):
        """return pathlib.Path for the project file"""        
        return self._vcxproj_file

    def projectName(self):
        """project name is the project file name without extension"""
        return self._vcxproj_file.stem

def Integrate(path):
    """
    Integrate '<projectName.>NmPackageDeps.props' into an '*.vcxproj' file

    path can be the path to a *.vcxproj file or a directory containing only one *.vcxproj file
    """
    vcxproj_filepath = find_vcxproj(path)

    integrate_vsproject(VsProject(vcxproj_filepath))

    
    
def find_vcxproj(path:Path)->Path:
    """
    *.vcxproj resolution:
        * if path is a *.vcxrpoj file then return it.
        * if path is a directory containing a single *.vcxproj file then return the *.vxcproj file
        * if path contains zero or multiple *.vcxproj files then an error is raises.
    """
    if path.is_file():
        if not path.match("*.vcxproj"):
            raise Exception("file is not a *.vcxproj file: "+ str(path))

        return path
    
    if path.is_dir():
        vcxprojectFiles = list(path.glob("*.vcxproj"))

        if len(vcxprojectFiles) == 1:
            return vcxprojectFiles[0]
        else:
            msg = "multiple project files found. specify single project on the command line."
            msg += "\n" + "/n  * ".join(vcxprojectFiles)
            raise Exception(msg)


from xml.dom import minidom
def integrate_vsproject(vsProject:VsProject):
    """
    Integrate '<projectName>.NmPackageDeps.props' into an `VsProject`

    create <projectName>.NmPackageDeps.props
    integrate into *.vcxproj file
    
    fail if  <projectName>.NmPackageDeps.props already exists
    """
    assert(Path(vsProject.path()).is_dir())

    packageDir = Path(__file__).parent


    # generate empty '<projectName>.NmPackageDeps.props' file
    target_file_path = vsProject.path() / Path(vsProject.projectName() + ".NmPackageDeps.props")
    if target_file_path.exists():
        raise Exception("Intergration failure. The following file already exists:\n    "+str(target_file_path))
    
    with open(target_file_path, 'wt') as f:
        f.write(VsProjectDependencySerialization.serialize())
    
    # read the project xml file
    projDom = minidom.parse(str(vsProject.projectFile()))

    # integrate the XXX.NmPackageDeps.props file into the project
    # i.e. add 
    #       <Import Project="XXX.NmPackageDeps.props" />
    # to the project file
    import_node = projDom.documentElement.appendChild(projDom.createElement("Import"))
    import_node.setAttribute("Project", target_file_path.name)


    # include the XXX.NmPackageDeps.props in the project file
    # i.e. add
    #       <ItemGroup>
    #         <Text Include="XXX.NmPackageDeps.props" />
    #       </ItemGroup>
    # to the project file
    group_node = projDom.documentElement.appendChild(projDom.createElement("ItemGroup"))
    text_node = group_node.appendChild(projDom.createElement("Text"))
    text_node.setAttribute("Include", target_file_path.name)


    # write the updated project xml config to file
    with open(vsProject.projectFile(), 'tw') as f:
        dom_str = projDom.toprettyxml(indent="  ", encoding="utf-8").decode()
        for line in dom_str.splitlines():
            # skip empty lines
            if not line.strip():
                continue

            # space before closing node tag
            #  NOK: <name attr="value"/>
            #  OK : <name attr="value" />
            # this appears to be the visual studio way                       
            line = line.replace('"/>', '" />')

            f.write(line + "\n")

def filehash(file):
    """compute file checksum"""
    h = hashlib.sha256()
    with open(file, 'rb') as f:
        h.update(f.read())
        return h.digest()


class NmPackageId(object):
    """
    A Nikon Metrology Package Identifier (NmPackage for short) is identified by <packageId> and a <versionId>
    """
    def __init__(self, packageId:str, versionId:str):
        self._packageId = packageId
        self._versionId = versionId

    @property
    def packageId(self) -> str :
        return self._packageId

    @property
    def versionId(self) -> str : 
        return self._versionId

    @property
    def path(self) -> str:
        """
        path to the System Wide package properties file
        """
        return r"$(NmPackageDir)\{packageId}\{versionId}\NmPackage.props".format(
            packageId = self.packageId,
            versionId = self.versionId)

    
    def __repr__(self) -> str:
        return "NmPackageId({}, {})".format(self.packageId, self.versionId)

    def __eq__(self, other) -> bool:
        return self.packageId == other.packageId and \
               self.versionId == other.versionId
    
    def __hash__(self):
        return hash(self.path)

class VsProjectDependencySerialization(object):
    """
    Serialize and deserialize a list of `NmPackageId`s to an MsBuild properties xml 
    """
    __comment = r"""
Nikon Metrology packages dependency listing

WARNING: AUTO GENERATED FILE, PLEASE DO NOT EDIT MANUALLY BUT USE THE NMPKG TOOL INSTEAD!!

This file should be included in the project file (*.vcxproj) that lives in the same folder as this file.

    <Import Project="<ProjectName>.NmPackageDeps.props" Condition="exists('<projectName>.NmPackageDeps.props')" />

All the Nikon Metrology package property sheets that are depended on by this project are listed here.
A dependency  on 'packageId' is expressed as follows.

    <Import Project="$(NmPackageDir)\<packageId>\<versionId>\NmPackage.props" Condition="exists('$(NmPackageDir)\<packageId>\<versionId>\NmPackage.props')" />

the condition is needed to allow the project to be loaded if the package is not yet present on the disk
"""
    @staticmethod
    def deserialize( xml : str) -> set:
        """
        parse a '<projectName>.NmPacakageDeps.props' xml stream adn return the set of `NmPackageId`s
        TODO: generalize to use IO streams to make it easy to unit test (read from in-mem string stream instead of a file)
        yet also type safe!
        """
        from xml.dom import minidom, Node
        dom = minidom.parseString(xml)
        print(dom)
        nmPackageIds = set()
        for c in dom.documentElement.childNodes:
            
            if c.nodeType == Node.COMMENT_NODE:
                # a comment node is expected and ignored
                continue
            elif c.nodeType == Node.TEXT_NODE:
                # TODO: what exactly are text nodes? this seems to be normal though!?
                continue
            
            # all other child nodes should be "Import" elements
            # Bail-Out if any other nodetype is found!
            # I.e. encourage the user of the NmPkg tool to edit this file maximizing consistency
            # and preventing misuse of the file for other purposes.
            if c.nodeType != Node.ELEMENT_NODE:
                raise Exception("unknown node: " + str(c))
            if c.tagName != "Import":
                raise Exception("Node with unknown tag (expected 'Import' tag): " + c.tagName)

            # attempt to deserialize the import_node
            nmPackage = VsProjectDependencySerialization._deserializer_NmPackageId(c)
            nmPackageIds.add(nmPackage)

        return nmPackageIds


    @staticmethod
    def _deserializer_NmPackageId(import_node) -> NmPackageId:
        r"""
        Desirializet an import xml element to an `NmPackageId`

           <Import Project="$(NmPackageDir)\<packageId>\<versionId>\NmPackage.props" 
                   Condition="exists('$(NmPackageDir)\<packageId>\<versionId>\NmPackage.props')" />
        """
        assert "Import" == import_node.tagName
        print("project: " + import_node.getAttribute("Project"))
        package_path = Path(import_node.getAttribute("Project"))
        print("package_path: " + str(package_path) )
        
        # break path into parts
        propsFile = package_path.name
        versionId = package_path.parent.name
        packageId = package_path.parent.parent.name
        PackageDir = package_path.parent.parent.parent.name

        # create NmPackageId
        nmPackageId  = NmPackageId(packageId, versionId)

        # check that all whole path was parsed
        if nmPackageId.path != str(package_path):
            raise Exception(r"""Path has wrong format:
expected: $(NmPackageDir)\<packageId>\<versionId>\NmPackage.props
actual  : {}
parsed  : {}""".format(
            str(package_path), nmPackageId.path))

        return nmPackageId


    @staticmethod
    def serialize(packages: set = set()) -> str:
        """
        Serialize a set of `NmPackageId`s to a '<ProjectName>.NmPackageDeps.props` xml stream
        """
        # create xml document
        from xml.dom import minidom
        dom = minidom.getDOMImplementation().createDocument(None, "Project", None)        
        dom.documentElement.setAttribute("DefaultTargets", "Build")
        dom.documentElement.setAttribute("ToolsVersion", "4.0")
        dom.documentElement.setAttribute("xmlns", "http://schemas.microsoft.com/developer/msbuild/2003")

        # add comment node
        dom.documentElement.appendChild(dom.createComment(VsProjectDependencySerialization.__comment))

        # sort packages alphabetically
        # this will make it eaiser for humans to find a package
        # it also ensures that if a non-empty VCS diff is an actual change and not just a reordering
        path_as_key = lambda nmPackageId: nmPackageId.path
        sorted_packages = sorted(packages, key=path_as_key )     

        # add Import nodes to dom
        for e in sorted_packages:
            import_node = dom.documentElement.appendChild(dom.createElement("Import"))
            import_node.setAttribute("Project", e.path)
            import_node.setAttribute("Condition", "Exists('{}')".format(e.path))

        # pretty print
        return dom.toprettyxml(indent="  ", encoding="utf-8").decode()

