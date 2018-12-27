import unittest
from pathlib import Path

from NmPackage import *
import os
import shutil

import xml.etree.ElementTree as ET

from NmPackage.test import *

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
            integrate_vsproject(VsProject(vsProjectPath))

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
            integrate_vsproject(VsProject(p.absolute().joinpath("Vs2017Project.vcxproj")))


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
            integrate_vsproject(VsProject(p.absolute().joinpath("Vs2017Project.vcxproj")))


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
            integrate_vsproject(VsProject(p.absolute().joinpath("Vs2017Project.vcxproj")))

            compare_dirs(verifiedDir, Path(tmpdir))


    def test_integrate_given_dir(self, tmpdir):
        """
        check that a directory containing a single *.vcxproj file can be integrated
        """
        self.setUp(tmpdir)
        verifiedDir = self.testFilesVerified.absolute()
        with chdir(Path(tmpdir) / Path("Vs2017Project")) as p:
            # test
            Integrate(p.absolute())
            
            compare_dirs(verifiedDir, Path(tmpdir))



if __name__ == '__main__':
    import pytest
    pytest.main()