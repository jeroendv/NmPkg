from pathlib import Path, PureWindowsPath
from xml.dom import minidom

from NmPackage import *


class VsProjectFiler(object):
    """
    (De)Serializing a `VsProject` from and to disk.

    It consists of two files:
      * <projectName>.vcxproj (e.g. `VcxProjectFileFormat`)
      * <projectName>.NmPackageDeps.props (e.g. `NmPackageDepsFileFormat`)

    """

    def serialize(self, vsProject: VsProject):
        # ensure the <projectName>.NmPacakgeDeps.props is imported in the *.vcxproj file
        vcx_project_file = VcxProjectFile(vsProject.project_filepath)
        vcx_project_file.integrate_nmpkg()

        # write the dependecies to disk
        propsfile = vsProject.project_filepath.with_name(
            vsProject.projectName + ".NmPackageDeps.props")
        with Path(propsfile).open("tw+") as f:
            f.write(NmPackageDepsFileFormat.serialize(vsProject.dependencies))

    def deserialize(self, vcxproject_filepath: Path):
        # create project file
        vcxproject_file = VcxProjectFile(vcxproject_filepath)
        # check if there are any package dependencies
        if not vcxproject_file.nmPackageDeps_path.is_file():
            return VsProject(vcxproject_filepath)

        # read package dependencies
        with vcxproject_file.nmPackageDeps_path.open("tr") as f:
            nmPackageIds = NmPackageDepsFileFormat.deserialize(f.read())
            vsProject = VsProject(vcxproject_filepath)
            vsProject.get_dependencies().update(nmPackageIds)

            return vsProject


def Integrate(path: Path):
    """
    Integrate '<projectName.>NmPackageDeps.props' into an '*.vcxproj' file

    path can be the path to a *.vcxproj file or a directory containing only one *.vcxproj file
    """
    vcxproj_filepath = find_vcxproj(Path(path))

    VsProjectFiler().serialize(VsProject(vcxproj_filepath))


def find_vcxproj(path: Path)->Path:
    """
    *.vcxproj resolution:
        * if path is a *.vcxrpoj file then return it.
        * if path is a directory containing a single *.vcxproj file then return the *.vxcproj file
        * if path contains zero or multiple *.vcxproj files then an error is raises.
    """
    if path.is_file():
        if not path.match("*.vcxproj"):
            raise Exception("file is not a *.vcxproj file: " + str(path))

        return path

    if path.is_dir():
        vcxprojectFiles = list(path.glob("*.vcxproj"))

        if len(vcxprojectFiles) == 1:
            return vcxprojectFiles[0]
        elif len(vcxprojectFiles) == 0:
            msg = "no project files found in the given directory:\n"
            msg += str(path)
            raise Exception(msg)
        else:
            assert len(vcxprojectFiles) > 1
            msg = "multiple project files found. specify single project on the command line."
            msg += "\n" + "/n  * ".join([str(f) for f in vcxprojectFiles])
            raise Exception(msg)

    msg = "unknown argument: " + str(path) + "\n"
    msg += "expected *.vcxproj file or dir containing a single *.vcxproj file"
    raise Exception(msg)


class VcxProjectFile(object):
    """Class representing an actual *.vcxproj file"""

    @property
    def path(self) -> Path:
        return self._path

    @property
    def nmPackageDeps_path(self):
        dir = self.path.parent
        projectName = self.path.stem
        return dir / Path(projectName + ".NmPackageDeps.props")

    def __init__(self, vcxproject_file_path: Path):
        """
        Create object given the path to an *.vcxproj file
        """
        self._path = Path(vcxproject_file_path)

        if not self.path.is_file():
            raise Exception("not a file: " + str(self.path))

        if not self.path.match("*.vcxproj"):
            raise Exception("not a vcxfile: " + str(self.path))

    def integrate_nmpkg(self):
        """
        Integrate '<projectName>.NmPackageDeps.props' into this *.vcxproj file
        """
        assert(self.path.exists())
        assert(self.path.match("*.vcxproj"))

        # read the project xml file
        with self.path.open("rt") as f:
            projDom = minidom.parse(f)

        # add property file to project
        self._import_NmPackageDeps(projDom)
        self._include_NmPackgeDeps(projDom)

        # write the updated project xml config to file
        sanitize_text_nodes(projDom.documentElement)
        with Path(self.path).open('tw') as f:
            dom_str = projDom.toprettyxml(
                indent="  ", encoding="utf-8").decode()
            for line in dom_str.splitlines():
                # space before closing node tag
                #  NOK: <name attr="value"/>
                #  OK : <name attr="value" />
                # this appears to be the visual studio way
                line = line.replace('"/>', '" />')

                f.write(line + "\n")

    def _import_NmPackageDeps(self, projDom):
        """
        integrate the XXX.NmPackageDeps.props file into the project
        i.e. add
              <Import Project="XXX.NmPackageDeps.props" />
        to the project file
        """
        # check if the file is not already imported
        for e in projDom.getElementsByTagName("Import"):
            if e.getAttribute("Project") == self.nmPackageDeps_path.name:
                # already imported, nothign to do!
                return

        # not yet imported add import element
        import_node = projDom.documentElement.appendChild(
            projDom.createElement("Import"))
        import_node.setAttribute("Project", self.nmPackageDeps_path.name)

    def _include_NmPackgeDeps(self, projDom: minidom.Document):
        """
        include the XXX.NmPackageDeps.props in the project file
        i.e. add
              <ItemGroup>
                <Text Include="XXX.NmPackageDeps.props" />
              </ItemGroup>
        to the project file
        """
        # check if the file is already included
        for e in projDom.getElementsByTagName("Text"):
            if e.getAttribute("Include") == self.nmPackageDeps_path.name \
               and e.parentNode.tagName == "ItemGroup":
                # already imported, nothing to do!
                return

        group_node = projDom.documentElement.appendChild(
            projDom.createElement("ItemGroup"))
        text_node = group_node.appendChild(projDom.createElement("Text"))
        text_node.setAttribute("Include", self.nmPackageDeps_path.name)


def sanitize_text_nodes(xml_element: minidom.Element):
    """
    remove empty xml text-nodes from complex element-nodes

    a simple element node does not contain child nodes. I.e. its data is the text.
    E.g. name is a simple node, "John Do" is its data

        <name>John Do</name>

    a complext element node is a container for child element nodes.
    I.e. its data is expressed by the child nodes and it should not have any text nodes of itself
    e.g. name is a complex node consisting of two simple nodes first and last

        <name><first>John</first><last>Do</last></name>

    when pretty printing a dom then such text nodes will result in empty lines!
    """
    from xml.dom import Node
    # from xml.dom.minidom import Element

    assert xml_element.nodeType == Node.ELEMENT_NODE

    child_element_nodes = [
        c for c in xml_element.childNodes if c.nodeType == Node.ELEMENT_NODE]

    # `xml_element` is a 'simple element', i.e. it has no child element nodes
    # Any text nodes are to be left as is since they represent this 'simple elements' data
    if not child_element_nodes:
        # nothing to do
        return

    # `xml_element` is a 'complext element`
    assert len(child_element_nodes) > 0

    # remove all empty text-nodes from this 'complex element'
    text_nodes = [
        c for c in xml_element.childNodes if c.nodeType == Node.TEXT_NODE]
    for t in text_nodes:
        if t.data.strip() == "":
            xml_element.removeChild(t)
            t.unlink()

    # recursively clean child element nodes
    for c in child_element_nodes:
        sanitize_text_nodes(c)


class NmPackageDepsFileFormat(object):
    """
    (De)Serializing a set of `NmPackageId`'s from and to NmPackageDeps.props file format.

    The NmPackageDeps.props file format is an msbuild property sheet with the sole concern of importing
    the property sheets of NmPackages.
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
    def deserialize(xml: str) -> set:
        """
        parse a '<projectName>.NmPacakageDeps.props' xml stream adn return the set of `NmPackageId`s
        TODO: generalize to use IO streams to make it easy to unit test (read from in-mem string stream instead of a file)
        yet also type safe!
        """
        from xml.dom import minidom, Node
        dom = minidom.parseString(xml)
        nmPackageIds = set()
        for c in dom.documentElement.childNodes:

            if c.nodeType == Node.COMMENT_NODE:
                # a comment node is expected and ignored
                continue
            elif c.nodeType == Node.TEXT_NODE:
                if c.data.strip() == "":
                    # empty text nodes are harmless in the NmPackageDeps.props file format
                    continue
                else:
                    raise Exeption(
                        "Unexpected text node under 'Project' root node.  (corrupted file?)")

            # all other child nodes should be "Import" elements
            # Bail-Out if any other nodetype is found!
            # I.e. encourage the user of the NmPkg tool to edit this file maximizing consistency
            # and preventing misuse of the file for other purposes.
            if c.nodeType != Node.ELEMENT_NODE:
                raise Exception("unknown node: " + str(c))
            if c.tagName != "Import":
                raise Exception(
                    "Node with unknown tag (expected 'Import' tag, corrupted file?): " + c.tagName)

            # attempt to deserialize the import_node
            nmPackage = NmPackageDepsFileFormat._path_to_package(
                c.getAttribute("Project"))
            nmPackageIds.add(nmPackage)

        return nmPackageIds

    @staticmethod
    def _package_to_path(nmPackageId: NmPackageId) -> str:
        """
        Convert a NmPackageId to an xml 'project/import@project' value according the NmPackageDeps.props file format

        See Also `_path_to_package` which does the reverse
        """
        package_path = PureWindowsPath("$(NmPackageDir)").joinpath(
            PureWindowsPath(nmPackageId.packageId)).joinpath(
            PureWindowsPath(nmPackageId.versionId)).joinpath(
            PureWindowsPath("NmPackage.props"))
        return str(package_path)

    @staticmethod
    def _path_to_package(path: str) -> NmPackageId:
        """
        Convert an xml 'project/import@project' value to a NmPackageId according the NmPackageDeps.props file format

        See Also `_package_to_path` which does the reverse
        """
        from pathlib import PureWindowsPath
        windows_path = PureWindowsPath(path)

        # the package path is essentially a windows path so lets break it into its 4 parts to process it
        propsFile = windows_path.name
        versionId = windows_path.parent.name
        packageId = windows_path.parent.parent.name
        PackageDir = windows_path.parent.parent.parent.name

        # create NmPackageId
        nmPackageId = NmPackageId(packageId, versionId)

        # check that all whole path was parsed
        # by verifying that the parsed paths is identical to the input path
        parsed_package_path = NmPackageDepsFileFormat._package_to_path(
            nmPackageId)
        if parsed_package_path != path:
            raise Exception("Failed to parse Project/Import@Project: " + path)

        return nmPackageId

    @staticmethod
    def serialize(packages: set = set()) -> str:
        """
        Serialize a set of `NmPackageId`s according the NmPackageDeps.props file format
        """
        # create xml document
        from xml.dom import minidom
        dom = minidom.getDOMImplementation().createDocument(None, "Project", None)
        dom.documentElement.setAttribute("DefaultTargets", "Build")
        dom.documentElement.setAttribute("ToolsVersion", "4.0")
        dom.documentElement.setAttribute(
            "xmlns", "http://schemas.microsoft.com/developer/msbuild/2003")

        # add comment node
        dom.documentElement.appendChild(
            dom.createComment(NmPackageDepsFileFormat.__comment))

        # sort packages alphabetically
        # this will make it eaiser for humans to find a package
        # it also ensures that if a non-empty VCS diff is an actual change and not just a reordering
        sorted_packages = sorted(
            packages, key=lambda nmPackageId: nmPackageId.qualifiedId)

        # add Import nodes to dom
        for p in sorted_packages:
            package_path = NmPackageDepsFileFormat._package_to_path(p)
            import_node = dom.documentElement.appendChild(
                dom.createElement("Import"))
            import_node.setAttribute("Project", package_path)
            import_node.setAttribute(
                "Condition", "Exists('{}')".format(package_path))

        # pretty print
        return dom.toprettyxml(indent="  ", encoding="utf-8").decode()
