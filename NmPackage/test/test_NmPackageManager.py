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
    assert "git@PC-CI-2.mtrs.intl:nmpackages/p_1.0.0.git" == url


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


class Test_NmPackageManager:

    package_cache_dir_fixture = \
        (Path(__file__).parent /
         Path("TestFiles/NmPackageManager/PackageCacheWithSomePackages")).absolute()

    package1_100 = NmPackageId("package1", "v1.0.0")
    package1_101 = NmPackageId("package1", "v1.0.1")
    package2_100 = NmPackageId("package2", "v1.0.0")

    def setUp(self, tmpdir):
        """Copy `testFilesPre` to the test dir `tmpdir`"""
        print(str(tmpdir))
        assert self.package_cache_dir_fixture.is_dir()
        from distutils.dir_util import copy_tree
        copy_tree(self.package_cache_dir_fixture, str(tmpdir))

    def test_get_installed_packages(self, tmpdir):
        # GIVEN a package cache with some pre-installed packages
        self.setUp(tmpdir)
        mgr = NmPackageManager(Path(str(tmpdir)))

        # WHEN getting all packages
        packages = mgr.get_installed_packages()

        # THEN there are 3 installed packages
        assert 3 == len(packages)
        assert self.package1_100 in packages
        assert self.package1_101 in packages
        assert self.package2_100 in packages

    def test_is_installed(self, tmpdir):
        # GIVEN a package cache with some pre-installed packages
        self.setUp(tmpdir)
        mgr = NmPackageManager(Path(str(tmpdir)))

        # THEN  the following packages should already be installed
        assert mgr.is_installed(self.package1_100)
        assert mgr.is_installed(self.package1_101)
        assert mgr.is_installed(self.package2_100)

    def test_uninstall(self, tmpdir):
        # GIVEN a package cache with some pre-installed packages
        self.setUp(tmpdir)
        mgr = NmPackageManager(Path(str(tmpdir)))

        # THEN  the following packages should already be installed
        assert mgr.is_installed(self.package1_100)
        assert mgr.is_installed(self.package1_101)
        assert mgr.is_installed(self.package2_100)

        # WHEN uninstalling a package
        mgr.uninstall(self.package2_100)

        # THEN the package is no longer present
        assert 2 == len(list(mgr.get_installed_packages()))
        assert not mgr.is_installed(self.package2_100)
        assert mgr.is_installed(self.package1_100)
        assert mgr.is_installed(self.package1_101)

        # WHEN uninstalling a second package
        mgr.uninstall(self.package1_101)

        # THEN the package is no longer present
        assert 1 == len(list(mgr.get_installed_packages()))
        assert not mgr.is_installed(self.package2_100)
        assert mgr.is_installed(self.package1_100)
        assert not mgr.is_installed(self.package1_101)

        # WHEN uninstalling a third and last package
        mgr.uninstall(self.package1_100)

        # THEN the list of installed packages is empty
        assert 0 == len(list(mgr.get_installed_packages()))
        assert not mgr.is_installed(self.package2_100)
        assert not mgr.is_installed(self.package1_100)
        assert not mgr.is_installed(self.package1_101)

        # THEN the package cache dir is empty
        assert 0 == len(list(mgr.package_cache_dir.iterdir()))

    def test_uninstall_non_existing_package(self, tmpdir):
        # GIVEN a package cache with some pre-installed packages
        self.setUp(tmpdir)
        mgr = NmPackageManager(Path(str(tmpdir)))
        assert 3 == len(list(mgr.get_installed_packages()))

        # GIVEN a non-installed package
        p = NmPackageId("non-installed_package", "1.0.0")
        assert not mgr.is_installed(p)

        # WHEN uninstalling said package
        mgr.uninstall(p)

        # THEN this a noop (i.e. it does not raise expections )
        # and all the originall installed packages are unaffected
        assert 3 == len(list(mgr.get_installed_packages()))
        

