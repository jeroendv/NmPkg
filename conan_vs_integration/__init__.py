
import os,sys
from pathlib import Path
import hashlib
import binascii
import shutil


class MsBuild:
    
    def Error(msg):
        """print an MSBuild error message to stderr"""
        sys.stderr.write("Error: " + msg)



class DebugLogScopedPush:
    def __init__(self, msg = None):
        self.msg = msg

    def __enter__(self):
        if(self.msg is not None):
            DebugLog.print(self.msg)
            
        self.originalIndentLvl = DebugLog.indentLvl
        DebugLog.push()
    
    def __exit__(self, type, value, traceback):
        DebugLog.pop()
        assert(DebugLog.indentLvl == self.originalIndentLvl)

class DebugLog:
    """An indentation aware debug log stream"""

    indentLvl = 0
    enabled = False

    def print(msg):
        # skip debug messages if debug mode is not enabled!
        if (not DebugLog.enabled):
            return 

        print("   "*DebugLog.indentLvl + msg)

    def push():
        DebugLog.indentLvl += 1
        return DebugLog.indentLvl

    def scopedPush(msg = None):
        return DebugLogScopedPush(msg)

    def pop():
        newIndentLvl = DebugLog.indentLvl - 1
        # indentLvl can't become negative
        if newIndentLvl < 0:
            newIndentLvl = 0
        
        DebugLog.indentLvl = newIndentLvl

        return DebugLog.indentLvl



class VsProject:
    """A Visual Studio project with a given name"""
    def __init__(self, path):
        self._set_path(path)

    def _set_path(self, path):
        self.path = os.path.abspath(path)

        if (not os.path.isdir(self.path)):
            raise Exception("'%s' is not an existing directory" % path)




class VerifyIntegration:

    def __init__(self, vsProject):
        self.vsProject = vsProject
        self.messages = []

    def verify(self):
        """verify an integration
        returns a failure message or None if all is ok
        """
        assert(os.getcwd() == self.vsProject.path)

        packageDir = Path(__file__).parent

        if (not os.path.isfile("Conan.targets")):
            return r"""No 'Conan.Targets' file found.
            Use the 'integrate' command to generate the file."""

        return self._verifyFileChecksum("Conan.targets")



    def _verifyFileChecksum(self, file):
        """verify a file checksum
        returns a failure message or None if all is ok
        """
        packageDir = Path(__file__).parent
        refFile = packageDir / file
        userFile = Path(os.getcwd()) / file

        # both the reference and the user file should exists
        assert(os.path.isfile(refFile))
        assert(os.path.isfile(userFile))

        with DebugLog.scopedPush("checking hash for file '%s'" % file):
            refFileDigest = filehash(refFile)
            userFileDigest = filehash(userFile)

            if refFileDigest != userFileDigest:
                DebugLog.print("hash mismatch!")
                DebugLog.print("referenceFile: " + binascii.hexlify(refFileDigest).decode('ascii'))
                DebugLog.print("userFile     : " + binascii.hexlify(userFileDigest).decode('ascii'))
                
                return """{file} has been illegally modified.
                The Conan.Targets file is an auto generated file from the 'integrate' command. It may not be modified.
                Use the 'integrate -u' command to regenerate the file.""".format(
                    file = file
                )
            else:
                DebugLog.print("hash match! => file is up to date")
                return None


def UpdateIntegration(vsProject):
    assert(os.getcwd() == vsProject.path)

    packageDir = Path(__file__).parent
    refFile = packageDir / "Conan.targets"
    shutil.copy(refFile, os.getcwd())

    refFile = packageDir / "ConanVsIntegration.Debug.targets"
    shutil.copy(refFile, os.getcwd())

def filehash(file):
    """compute file checksum"""
    h = hashlib.sha256()
    with open(file, 'rb') as f:
        h.update(f.read())
        return h.digest()



