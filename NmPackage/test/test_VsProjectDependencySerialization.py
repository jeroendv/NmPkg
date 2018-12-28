"""
Unit test for `VsProjectDependencySerialization`
"""

import pytest
import unittest
from NmPackage import NmPackageId
from NmPackage import VsProjectDependencySerialization


package_A_1 = NmPackageId("packageA", "1")
package_A_2 = NmPackageId("packageA", "2")

xml_0_deps = r"""<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <!--
Nikon Metrology packages dependency listing

WARNING: AUTO GENERATED FILE, PLEASE DO NOT EDIT MANUALLY BUT USE THE NMPKG TOOL INSTEAD!!

This file should be included in the project file (*.vcxproj) that lives in the same folder as this file.

    <Import Project="<ProjectName>.NmPackageDeps.props" Condition="exists('<projectName>.NmPackageDeps.props')" />

All the Nikon Metrology package property sheets that are depended on by this project are listed here.
A dependency  on 'packageId' is expressed as follows.

    <Import Project="$(NmPackageDir)\<packageId>\<versionId>\NmPackage.props" Condition="exists('$(NmPackageDir)\<packageId>\<versionId>\NmPackage.props')" />

the condition is needed to allow the project to be loaded if the package is not yet present on the disk
-->
</Project>
"""

xml_1_deps = r"""<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <!--
Nikon Metrology packages dependency listing

WARNING: AUTO GENERATED FILE, PLEASE DO NOT EDIT MANUALLY BUT USE THE NMPKG TOOL INSTEAD!!

This file should be included in the project file (*.vcxproj) that lives in the same folder as this file.

    <Import Project="<ProjectName>.NmPackageDeps.props" Condition="exists('<projectName>.NmPackageDeps.props')" />

All the Nikon Metrology package property sheets that are depended on by this project are listed here.
A dependency  on 'packageId' is expressed as follows.

    <Import Project="$(NmPackageDir)\<packageId>\<versionId>\NmPackage.props" Condition="exists('$(NmPackageDir)\<packageId>\<versionId>\NmPackage.props')" />

the condition is needed to allow the project to be loaded if the package is not yet present on the disk
-->
  <Import Condition="Exists('$(NmPackageDir)\packageA\2\NmPackage.props')" Project="$(NmPackageDir)\packageA\2\NmPackage.props"/>
</Project>
"""

xml_2_deps = r"""<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <!--
Nikon Metrology packages dependency listing

WARNING: AUTO GENERATED FILE, PLEASE DO NOT EDIT MANUALLY BUT USE THE NMPKG TOOL INSTEAD!!

This file should be included in the project file (*.vcxproj) that lives in the same folder as this file.

    <Import Project="<ProjectName>.NmPackageDeps.props" Condition="exists('<projectName>.NmPackageDeps.props')" />

All the Nikon Metrology package property sheets that are depended on by this project are listed here.
A dependency  on 'packageId' is expressed as follows.

    <Import Project="$(NmPackageDir)\<packageId>\<versionId>\NmPackage.props" Condition="exists('$(NmPackageDir)\<packageId>\<versionId>\NmPackage.props')" />

the condition is needed to allow the project to be loaded if the package is not yet present on the disk
-->
  <Import Condition="Exists('$(NmPackageDir)\packageA\1\NmPackage.props')" Project="$(NmPackageDir)\packageA\1\NmPackage.props"/>
  <Import Condition="Exists('$(NmPackageDir)\packageA\2\NmPackage.props')" Project="$(NmPackageDir)\packageA\2\NmPackage.props"/>
</Project>
"""

def test_empty_serialization():
    # GIVEN nothing

    # WHEN serializing noting
    xml_out = VsProjectDependencySerialization.serialize()

    # THEN the output is the empty <projectName>.NmPackageDeps.props template
    assert xml_0_deps == xml_out

def test_1_serialization():
    # GIVEN a single package

    # WHEN serializing that package
    xml_out = VsProjectDependencySerialization.serialize([package_A_2])

    # THEN the output should match the expected output
    assert xml_1_deps == xml_out


def test_2_serialization_order():
    # GIVEN two packages

    # WHEN serializing those packages passing them in different order
    xml_out1 = VsProjectDependencySerialization.serialize([package_A_2, package_A_1])
    xml_out2 = VsProjectDependencySerialization.serialize([package_A_1, package_A_2])

    # THEN the output is ordered (alphabetically) so the outpt is the same
    assert xml_2_deps == xml_out1
    assert xml_2_deps == xml_out2


def test_empty_deserialization():
    # GIVEN an empty props file
    xml_in = xml_0_deps

    # WHEN deserializing 
    nmPackages = VsProjectDependencySerialization.deserialize(xml_in)

    # THEN an empty set is returned
    assert  not nmPackages

def test_1_deserialization():
    # GIVEN a props file with a single dependency
    xml_in = xml_1_deps

    # WHEN deserializing 
    nmPackages = VsProjectDependencySerialization.deserialize(xml_in)

    # THEN a set with a single package is returned
    assert  set([package_A_2]) == nmPackages


def test_2_deserialization_order():
    # GIVEN a props file with a two dependency
    xml_in = xml_2_deps

    # WHEN deserializing 
    nmPackages = VsProjectDependencySerialization.deserialize(xml_in)

    # THEN a set with a the two package is returned
    assert  set([package_A_1, package_A_2]) == nmPackages






