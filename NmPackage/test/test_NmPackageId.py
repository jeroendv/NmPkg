from NmPackage import NmPackageId


def test_getters():
    # GIVEN a NmPakageId
    p = NmPackageId("A", "1")

    # THEN verify the various getters
    assert "A" == p.packageId
    assert "1" == p.versionId
    assert r"A\1" == p.qualifiedId
    assert 'NmPackageId("A", "1")' == repr(p)


def test_equality():
    assert NmPackageId("A", "1") == NmPackageId('A', '1')

    assert NmPackageId("A", "1") != NmPackageId('A', '2')
    assert NmPackageId("A", "1") != NmPackageId('B', '1')
    assert NmPackageId("A", "1") != NmPackageId('a', '1')


def test_hash():
    assert hash(NmPackageId), "verify that NmPackageId has a hash implementation"
