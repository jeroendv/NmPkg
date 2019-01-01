"""
"""


def test_Pathlib_PureWindowsPath():
    """
    Test pathlib.Path parent properties
    """
    from pathlib import PureWindowsPath

    p = PureWindowsPath(
        r"$(NmPackageDir)/<packageId>/<versionId>/NmPackage.props")
    assert r"$(NmPackageDir)\<packageId>\<versionId>\NmPackage.props" == str(p)
    assert "NmPackage.props" == p.name

    p = p.parent
    assert r"$(NmPackageDir)\<packageId>\<versionId>" == str(p)
    assert "<versionId>" == p.name

    p = p.parent
    assert r"$(NmPackageDir)\<packageId>" == str(p)
    assert "<packageId>" == p.name

    p = p.parent
    assert r"$(NmPackageDir)" == str(p)
    assert "$(NmPackageDir)" == p.name
