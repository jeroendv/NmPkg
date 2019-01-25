from NmPackage import NmPackageManager
from NmPackage import NmPackageId
from pathlib import Path



def assert_git_project_slug(expected_git_slug: str, nm_package_id: NmPackageId):
    """assert the git projec slug of an NmPackageId"""
    # GIVEN an NmPackageId
    
    # WHEN building the git repo slug for that package
    slug = NmPackageManager.get_git_project_slug(nm_package_id)
    
    # THEN the slug should match the expected value 
    assert expected_git_slug == slug


def test_git_project_slugs_generation():
    # the package and versionId are separated by a _
    assert_git_project_slug("packageId_1.0.0-a", NmPackageId("packageId", "1.0.0-a"))

    # illegal chars are replaced with _
    # everything that is not a letter, digit, -, _, . is replaces
    assert_git_project_slug("package_with_spaces_1_0_0", NmPackageId("package with spaces", "1 0 0"))
    assert_git_project_slug("package_b_version_1_0_a", NmPackageId("package+b", "version:1,0%a"))

    # package can't start with -
    assert_git_project_slug("_package_1", NmPackageId("-package", "1"))
    assert_git_project_slug("_-package_1", NmPackageId("--package", "1"))


    # project slugs can't end with '.git' or '.atom'
    assert_git_project_slug("package_1_git", NmPackageId("package", "1.git"))
    assert_git_project_slug("package_2_atom", NmPackageId("package", "2.atom"))

    # other extensionlike versions are fine though
    assert_git_project_slug("package_3.jdv", NmPackageId("package", "3.jdv"))


def test_get_git_repo_url():
    # GIVEN an NmPackageId
    p = NmPackageId("p", "1.0.0")

    # THEN check the git repo url for that package
    url = NmPackageManager.get_git_repo_url(p)
    assert "git@PC-CI-2.mtrs.intl:nmpackages/p_1.0.0.git" ==  url

def test_get_package_dir():
    # GIVEN a package 
    p = NmPackageId("myPackage", "1.0.0")

    # THEN the package directory is constructed from the
    # packageId and the versionId
    path = NmPackageManager.get_package_dir(p)
    assert Path("myPackage") / (Path("1.0.0")) == path

    # the pathlib.Path should take care of the dir separators
    assert Path("myPackage/1.0.0") == path
    assert Path("myPackage\\1.0.0") == path
