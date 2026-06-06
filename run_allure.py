"""
Run behave with allure-behave formatter, patching the KeyError bug
in allure_commons that affects Python 3.13.
"""
import allure_commons.reporter as _reporter

# Patch: safely pop uuid instead of crashing with KeyError
_original_close_test = _reporter.AllureReporter.close_test


def _safe_close_test(self, uuid):
    if uuid not in self._items:
        return
    _original_close_test(self, uuid)


_reporter.AllureReporter.close_test = _safe_close_test

# Now run behave
import sys
import os

os.makedirs("reports/allure-results", exist_ok=True)

from behave.__main__ import main as behave_main

sys.argv = [
    "behave",
    "-f", "allure_behave.formatter:AllureFormatter",
    "-o", r"C:\Temp\allure-results",
]

sys.exit(behave_main())
