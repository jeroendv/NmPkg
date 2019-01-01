import sys
import traceback


def exception_handler(exception_type, exception, tb):
    """custom Exception handler for this cli that suppresses the stack trace by default"""
    # format python exception
    sys.stderr.write(
        "Error: " + str(exception_type.__name__) + " : " + str(exception))
    sys.stderr.write("\n")
    # print stack trace in debug mode only
    if (DebugLog.enabled):
        traceback.print_tb(tb)


class DebugLogScopedPush:
    def __init__(self, msg=None):
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
    enabled = True

    @staticmethod
    def print(msg):
        # skip debug messages if debug mode is not enabled!
        if DebugLog.enabled:
            print("|  " * DebugLog.indentLvl + msg, flush=True)

    @staticmethod
    def push():
        DebugLog.indentLvl += 1
        return DebugLog.indentLvl

    @staticmethod
    def pop():
        newIndentLvl = DebugLog.indentLvl - 1

        # indentLvl can't become negative
        if newIndentLvl < 0:
            newIndentLvl = 0

        DebugLog.indentLvl = newIndentLvl
        return DebugLog.indentLvl
