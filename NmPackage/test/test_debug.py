from NmPackage.debug import *


def test_for_syntax_errors():
    # WHEN performing a debug log print
    DebugLog.print("Boe")

    # Then the code should not  throw

def test_for_syntax_errors_2():
    # WHEN performing a debug log print
    with DebugLogScopedPush("Level 0"):
        DebugLog.print("Level 1")

    # Then the code should not  throw
