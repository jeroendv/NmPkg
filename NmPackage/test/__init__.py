from pathlib import Path
import sys


def compare_dirs(dir1: Path, dir2: Path):
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


def compare_files(file1: Path, file2: Path):
    """
    file comparison
     * print unified diff to std
     * assert failure if diff is not empty.
    """
    import difflib
    diff = difflib.unified_diff(file1.open("rt").readlines(
    ), file2.open("rt").readlines(), str(file1), str(file2))
    difflines = list(diff)
    sys.stdout.writelines(difflines)
    assert not difflines, "diff should be empty"
