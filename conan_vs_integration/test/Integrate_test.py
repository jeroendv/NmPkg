import unittest
from pathlib import Path

from conan_vs_integration import *
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


class integrat_test(unittest.TestCase):

    testFilesPre = Path(r"conan_vs_integration\test\TestFiles\VsProjectIntegration.pre")
    testFilesCurrent = testFilesPre.with_name("VsProjectIntegration.current")
    testFilesVerified = testFilesPre.with_name("VsProjectIntegration.verified")


    def setUp(self):
        # cleanup the test output dir and copy the textures
        if (self.testFilesCurrent.exists()):
            shutil.rmtree(self.testFilesCurrent)
        shutil.copytree(self.testFilesPre, self.testFilesCurrent)

    def test_creationOfFiles(self):
        """Verify  that that appropriate files are created
        """
        with chdir(self.testFilesCurrent / Path("Vs2017Project")) as p: 
            vsProjectPath = p.absolute()

            # Test pre-conditions
            self.assertFalse(Path("conanfile.txt").is_file(),
                msg="before integration there should not be a 'conanfile.txt'")
            self.assertFalse(Path("Conan.targets").is_file(),
                msg="before integration there should not be a 'Conan.targets'")

            # test
            Integrate(VsProject(vsProjectPath))

            # test post-conditions
            # verify that requried files were created
            self.assertTrue(Path("conanfile.txt").is_file(),
                msg="after integration a 'conanfile.txt' file should be present")
            self.assertTrue(Path("Conan.targets").is_file(),
                msg="after integration 'Conan.targets' file should be present")
        
    def test_TargetsIntegration(self):
        """Verify that the 'conan.targets' is properly imported in project file
        """
        with chdir(self.testFilesCurrent / Path("Vs2017Project")) as p:
            # test
            Integrate(VsProject(p.absolute()))


            # test post-conditions
            # search for the following node under projet file xml root 
            #       <Import Project="Conan.targets" />
            projTree = ET.parse(Path("VS2017Project.vcxproj"))
            root = projTree.getroot()
            ns = {'default': 'http://schemas.microsoft.com/developer/msbuild/2003'}

            for c in root.findall("default:Import", ns):
                print(c.tag, c.attrib)
                if ('Project' in c.attrib 
                    and c.get('Project') == 'Conan.targets'):
                    # node found :-)
                    return 
        
            self.fail(msg='no import node found that imports conan.targets')

    def test_conanFileIntegration(self):
        """Verify that the 'conafile.txt' is properly imported in project file
        """
        with chdir(self.testFilesCurrent / Path("Vs2017Project")) as p:
            # test pre-conditions
            pass

            # test
            Integrate(VsProject(p.absolute()))


            # test post-conditions
            # search for the following node under the project file xml root 
            #       <ItemGroup>
            #         <Text Include="conanfile.txt" />
            #       </ItemGroup>
            # to the project file
            projTree = ET.parse(Path("VS2017Project.vcxproj"))
            root = projTree.getroot()
            ns = {'default': 'http://schemas.microsoft.com/developer/msbuild/2003'}

            for c in root.findall("default:ItemGroup/default:Text", ns):
                print(c.tag, c.attrib)
                if ('Include' in c.attrib 
                    and c.attrib['Include'] == 'conanfile.txt'):
                    # node found :-)
                    return 
        
            self.fail(msg='conanfile.txt include is missing')















if __name__ == '__main__':
    unittest.main()
