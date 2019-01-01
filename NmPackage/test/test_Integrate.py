import pytest
from pathlib import Path
import os
import shutil

import xml.etree.ElementTree as ET

from NmPackage import *
from NmPackage.save import *
from NmPackage.test import *


class Test_Integrate:

    testFilesPre = (Path(__file__).parent /
                    Path("TestFiles/VsProjectIntegration.pre")).absolute()
    testFilesVerified = (Path(__file__).parent /
                         Path("TestFiles/VsProjectIntegration.verified")).absolute()

    def setUp(self, tmpdir):
        """Copy `testFilesPre` to the test dir `tmpdir`"""
        print(str(tmpdir))
        from distutils.dir_util import copy_tree
        copy_tree(self.testFilesPre, str(tmpdir))

    def test_creationOfFiles(self, tmpdir):
        """Verify  that that appropriate files are created"""
        # Given a clean VsProject
        self.setUp(tmpdir)
        p = Path(tmpdir) / Path("Vs2017Project")
        os.chdir(p)

        assert not Path("Vs2017Project.NmPackageDeps.props").is_file(), \
            "before integration there should not be a 'Vs2017Project.NmPackageDeps.props'"

        # WHEN Integrating into said project
        integrate_vsproject(VsProject(Path("Vs2017Project.vcxproj")))

        # THEN
        assert Path("Vs2017Project.NmPackageDeps.props").is_file(), \
            "after integration a 'Vs2017Project.NmPackageDeps.props' file should be present"

    def test_TargetsIntegration(self, tmpdir):
        """Verify that the 'Vs2017Project.NmPackageDeps.props' is properly imported in project file"""
        # Given a clean VsProject
        self.setUp(tmpdir)
        p = Path(tmpdir) / Path("Vs2017Project")
        os.chdir(p)

        # WHEN Integrating into the project folder
        integrate_vsproject(VsProject(Path("Vs2017Project.vcxproj")))

        # THEN the verify that the *.vcxproj file has an xml element Project/Import as follows
        #       <Import Project="Vs2017Project.NmPackageDeps.props" />
        projTree = ET.parse(Path("Vs2017Project.vcxproj"))
        root = projTree.getroot()
        ns = {'default': 'http://schemas.microsoft.com/developer/msbuild/2003'}

        found = False
        for c in root.findall("default:Import", ns):
            print(c.tag, c.attrib)
            if ('Project' in c.attrib
                    and c.get('Project') == 'Vs2017Project.NmPackageDeps.props'):
                # node found :-)
                found = True

        assert found, "no import node found that imports Vs2017Project.NmPackageDeps.props"

        # THEN the verify that the *.vcxproj file has an xml element Project/ItemGroup/Text as follows
        #       <ItemGroup>
        #         <Text Include="Vs2017Project.NmPackageDeps.props" />
        #       </ItemGroup>
        found = False
        for c in root.findall("default:ItemGroup/default:Text", ns):
            print(c.tag, c.attrib)
            if ('Include' in c.attrib
                    and c.attrib['Include'] == 'Vs2017Project.NmPackageDeps.props'):
                # node found :-)
                found = True

        assert found, "Vs2017Project.NmPackageDeps.props include is missing from *.vcxproj file"

    def test_regressionTest(self, tmpdir):
        """
        check if result of integration into:
                NmPackage\test\TestFiles\VsProjectIntegration.pre\Vs2017Project\
        equals the baseline result:
                NmPackage\test\TestFiles\VsProjectIntegration.verified\Vs2017Project\
        """
        # Given a clean VsProject
        self.setUp(tmpdir)
        p = Path(tmpdir) / Path("Vs2017Project")
        os.chdir(p)

        # WHEN Integrating into the project dir
        integrate_vsproject(VsProject(Path("Vs2017Project.vcxproj")))

        # THEN the resulting dir should match the baseline
        compare_dirs(self.testFilesVerified, Path(tmpdir))

    def test_integrate_given_dir(self, tmpdir):
        """
        check that a directory containing a single *.vcxproj file can be integrated
        """
        # GIVEN a clean dir with a single clean project
        self.setUp(tmpdir)
        verifiedDir = self.testFilesVerified.absolute()
        os.chdir(Path(tmpdir) / Path("Vs2017Project"))

        # WHEN Intregration into the dir
        Integrate(".")

        # THEN the result dir should be identical to the baseline
        compare_dirs(verifiedDir, Path(tmpdir))

    def test_cli_call(self, tmpdir):
        """
        check that a directory containing a single *.vcxproj file can be integrated though the command line
        """
        # given a clean project
        self.setUp(tmpdir)
        verifiedDir = self.testFilesVerified.absolute()
        os.chdir(Path(tmpdir) / Path("Vs2017Project"))

        # WHEN calling the cli main function with the debug option
        import NmPackage.cli.integrate
        sys.argv = ['arg0', '-d']
        NmPackage.cli.integrate.main()

        # THEN the result should match the baseline
        compare_dirs(verifiedDir, Path(tmpdir))


class Test_Integrate_error_flows():

    def test_fail_on_nonexisting_file(self):

        # WHEN integrating into a non-existing file
        with pytest.raises(Exception) as e:
            Integrate("non-existing_file.txt")

        # THEN this should fail with a proper error message
        assert "expected *.vcxproj file or dir containing a single *.vcxproj file" in str(
            e.value)

    def test_fail_for_non_vcxprojfile(self, tmpdir):
        os.chdir(str(tmpdir))
        # GIVEN a non *.vcxproj file
        non_vcxproj_file = Path("non-vcxprojFile.txt")
        with non_vcxproj_file.open("wt") as f:
            f.write("")

        # WHEN Integration into that file
        with pytest.raises(Exception) as e:
            Integrate("non-vcxprojFile.txt")

        # THEN this should fail with a proper error message
        assert "file is not a *.vcxproj file" in str(e.value)

    def test_fail_on_dir_without_project(self, tmpdir):
        os.chdir(str(tmpdir))
        # GIVEN a dir without a *.vxcproj file
        assert not list(Path(".").glob("*.vcxproj"))

        # WHEN integrating into the dir
        with pytest.raises(Exception) as e:
            Integrate(".")

        # THEN this should fail with a proper error message
        assert "no project files found in the given directory:" in str(e.value)

    def test_fail_on_dir_with_multiple_projects(self, tmpdir):
        os.chdir(tmpdir)
        # GIVEN a dir with multiple *.vcxprojects
        with Path("proj1.vcxproj").open("wt") as f:
            f.write("")

        with Path("proj2.vcxproj").open("wt") as f:
            f.write("")

        assert len(list(Path(".").glob("*.vcxproj"))) > 1

        # WHEN integrating into the dir
        with pytest.raises(Exception) as e:
            Integrate(".")

        # THEN this should fail with a proper error message
        assert "multiple project files found." in str(e.value)
