from pathlib import Path
from NmPackage import delete_tree
import os

def test_delete_tree(tmpdir):
    os.chdir(tmpdir)

    # GIVEN a directory with sub directoy an a file in each
    Path("rootDir/subDir").mkdir(parents=True)
    Path("rootDir/subDir/subfile.txt").touch()
    Path("rootDir/file.dat").touch()

    files = list(Path(".").glob("**/*"))
    assert 4 == len(files)

    # WHEN deleting the rootDir
    delete_tree(Path("rootDir"))

    # THEN nothing remains
    files = list(Path(".").glob("*"))
    assert 0 == len(files), "there should be no glob results"
    files2 = list(Path(".").iterdir())
    assert 0 == len(files2), "there should be no directory entries"


def test_delete_tree_with_readonly_file(tmpdir):
    os.chdir(tmpdir)

    # GIVEN a directory tree
    Path("rootDir/subDir").mkdir(parents=True)
    Path("rootDir/subDir/subfile.txt").touch(0o0400)  # read by owner
    Path("rootDir/file.dat").touch(0o0000) # no permisions for any-one

    files = list(Path(".").glob("**/*"))
    assert 4 == len(files)
    
    # GIVE|N that that a file has no write rights
    assert not os.access("rootDir/file.dat", os.W_OK)

    # GIVEN a file without any permissions
    Path("rootDir/subDir/subfile.txt").chmod(0o0000) # no permisions for any-one
    assert not os.access("rootDir/subDir/subfile.txt", os.W_OK)

    # WHEN deleting the rootDir
    delete_tree(Path("rootDir"))

    # THEN nothing remains
    files = list(Path(".").glob("*"))
    assert 0 == len(files), "there should be no glob results"
    files2 = list(Path(".").iterdir())
    assert 0 == len(files2), "there should be no directory entries"

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])