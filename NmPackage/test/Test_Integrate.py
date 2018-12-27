import unittest
from pathlib import Path

from NmPackage import *
import os
import shutil

import xml.etree.ElementTree as ET


class chdir():
    def __init__(self, newPath):
        self.newPath = newPath
    
    def __enter__(self):

        if (not Path(self.newPath).is_dir()):
            raise Exception("Can not change to a directory that does not exist.")

        self.oldPath = os.getcwd()
        os.chdir(self.newPath)
        return Path()

    def __exit__(self, type, value, tb):
        os.chdir(self.oldPath)


class Test_Integrate:

    testFilesPre = Path(r"NmPackage\test\TestFiles\VsProjectIntegration.pre")
    testFilesVerified = testFilesPre.with_name("VsProjectIntegration.verified")


    def setUp(self, tmpdir):
        print(str(tmpdir))
        from distutils.dir_util import copy_tree
        copy_tree(self.testFilesPre, str(tmpdir))

    def test_creationOfFiles(self, tmpdir):
        """Verify  that that appropriate files are created
        """
        self.setUp(tmpdir)
        with chdir(Path(tmpdir) / Path("Vs2017Project")) as p:
            vsProjectPath = p.absolute().joinpath("Vs2017Project.vcxproj")

            # Test pre-conditions
            assert not Path("Vs2017Project.NmPackageDeps.props").is_file(), \
                "before integration there should not be a 'Vs2017Project.NmPackageDeps.props'"

            # test
            Integrate(VsProject(vsProjectPath))

            # test post-conditions
            # verify that requried files were created
            assert Path("Vs2017Project.NmPackageDeps.props").is_file(), \
                "after integration a 'Vs2017Project.NmPackageDeps.props' file should be present"
        
    def test_TargetsIntegration(self, tmpdir):
        """Verify that the 'Vs2017Project.NmPackageDeps.props' is properly imported in project file
        """
        self.setUp(tmpdir)
        with chdir(Path(tmpdir) / Path("Vs2017Project")) as p:
            # test
            Integrate(VsProject(p.absolute().joinpath("Vs2017Project.vcxproj")))


            # test post-conditions
            # search for the following node under projet file xml root 
            #       <Import Project="Vs2017Project.NmPackageDeps.props" />
            projTree = ET.parse(Path("VS2017Project.vcxproj"))
            root = projTree.getroot()
            ns = {'default': 'http://schemas.microsoft.com/developer/msbuild/2003'}

            for c in root.findall("default:Import", ns):
                print(c.tag, c.attrib)
                if ('Project' in c.attrib 
                    and c.get('Project') == 'Vs2017Project.NmPackageDeps.props'):
                    # node found :-)
                    return
        
            assert False, "no import node found that imports Vs2017Project.NmPackageDeps.props"

    def test_conanFileIntegration(self, tmpdir):
        """Verify that the 'Vs2017Project.NmPackageDeps.props' is properly imported in project file
        """
        self.setUp(tmpdir)
        with chdir(Path(tmpdir) / Path("Vs2017Project")) as p:
            # test pre-conditions
            pass

            # test
            Integrate(VsProject(p.absolute().joinpath("Vs2017Project.vcxproj")))


            # test post-conditions
            # search for the following node under the project file xml root 
            #       <ItemGroup>
            #         <Text Include="Vs2017Project.NmPackageDeps.props" />
            #       </ItemGroup>
            # to the project file
            projTree = ET.parse(Path("VS2017Project.vcxproj"))
            root = projTree.getroot()
            ns = {'default': 'http://schemas.microsoft.com/developer/msbuild/2003'}

            for c in root.findall("default:ItemGroup/default:Text", ns):
                print(c.tag, c.attrib)
                if ('Include' in c.attrib 
                    and c.attrib['Include'] == 'Vs2017Project.NmPackageDeps.props'):
                    # node found :-)              
                    return 
        
            assert False, "Vs2017Project.NmPackageDeps.props include is missing from *.vcxproj file"

    def test_regressionTest(self, tmpdir):
        """
        check if result of integration into:
                NmPackage\test\TestFiles\VsProjectIntegration.pre\Vs2017Project\
        equals the baseline result:
                NmPackage\test\TestFiles\VsProjectIntegration.verified\Vs2017Project\
        """
        self.setUp(tmpdir)
        verifiedDir = self.testFilesVerified.absolute()
        with chdir(Path(tmpdir) / Path("Vs2017Project")) as p:
            # test
            Integrate(VsProject(p.absolute().joinpath("Vs2017Project.vcxproj")))

            compare_dirs(verifiedDir, Path(tmpdir))

def compare_dirs(dir1:Path, dir2:Path):
    """
    recursive directory comparison
    """
    # check that both inputs are dirs
    assert dir1.is_dir()
    assert dir2.is_dir()

    import filecmp
    dcmp = filecmp.dircmp(dir1, dir2)

    # dirs are no equal if there are unique files on the left or the right
    assert not dcmp.left_only, "there should be no left orphans"
    assert not dcmp.right_only, " there should be no right orphans"

    # compare the content of identically named files
    for file in dcmp.common_files:
        compare_files(dcmp.left / file, dcmp.right / file)

    # recurse into sub directories
    for dir in dcmp.common_dirs:
        compare_dirs(dcmp.left / dir, dcmp.right / dir)

def compare_files(file1:Path, file2:Path):
    """
    file comparison
     * print unified diff to std
     * assert failure if diff is not empty.
    """
    import difflib
    diff = difflib.unified_diff(file1.open("rt").readlines(), file2.open("rt").readlines(), str(file1), str(file2))
    difflines = list(diff)
    sys.stdout.writelines(difflines)
    assert not difflines, "diff should be empty"



if __name__ == '__main__':
    import pytest
    pytest.main()