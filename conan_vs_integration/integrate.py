import sys
import argparse
import os
from pathlib import Path
import shutil
import hashlib
import binascii

"""integrate conan into MSBuild for a given project
"""


def parse_cli_args():
    """parse the script input arguments"""
    global args
    parser = argparse.ArgumentParser(description = "Conan integration for Visual studio MSBuild")

    parser.add_argument("-v", "--verbose",
                    help="increase output verbosity",
                    action="store_true")

    parser.add_argument("-d","--debug",
                    help="enable debug output",
                    action="store_true")

    parser.add_argument("-N", "--dry-run",
                        help="Do not perform any actions, only simulate them.")

    # parser.add_argument("command",
    #                     help="which command to invoke"
    #                     nargs="?")
    args = parser.parse_args()
    if(args.debug):
        print("cli arguments: " + str(args)) 


    # don't show error trace in non-debug mode
    if(args.debug is False):
        sys.excepthook = exception_handler

def main():
    parse_cli_args()
    packageDir = Path(__file__).parent
    refFile = packageDir / "Conan.targets"
    userFile = Path(os.getcwd()) / "Conan.targets"

    if (userFile.exists()):
        updateIfChanged(refFile, userFile)
    else:
        if args.debug:
            print("file missing => installing file")
        shutil.copyfile(refFile, userFile)
        sys.stderr.write("error: Conan.Targets' was integrated. restart build is required!")
        sys.exit(1)


def updateIfChanged(src, dst):
    srcDigest = filehash(src)
    dstDigest = filehash(dst)
    
    if srcDigest != dstDigest:
        if args.debug:
            print("hash mismatch! => updating file")
            print("srcFile: " + binascii.hexlify(srcDigest).decode('ascii'))
            print("dstFile: " + binascii.hexlify(dstDigest).decode('ascii'))
        
       
        shutil.copyfile(src, dst)
        sys.stderr.write("error: Conan.Targets' was updated. restart build is required!")
        sys.exit(1)
    else:
         if args.debug:
            print("hash match! => file is up to date")

def filehash(file):
    h = hashlib.sha256()
    with open(file, 'rb') as f:
        h.update(f.read())
        return h.digest()
    








def exception_handler(exception_type, exception, traceback):
    # All your trace are belong to us!
    # your format
    print(str(exception_type.__name__) + " : " + str(exception))




