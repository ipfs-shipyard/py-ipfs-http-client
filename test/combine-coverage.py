#!/usr/bin/python3
import glob
import os
import pathlib

import coverage

# Monkey-patch `coverage` to not randomly delete files
import coverage.data
coverage.data.file_be_gone = lambda *a: None

# Switch working directory to project directory
BASE_PATH = pathlib.Path(__file__).parent.parent
DATA_PATH = BASE_PATH / "coverage"
os.chdir(str(BASE_PATH))


cov = coverage.Coverage()

# Load the most recent coverage data collected for each test platform
cov.combine(glob.glob("build/test-py*/cov_raw"), strict=True)

cov.report()
cov.html_report(directory=str(DATA_PATH / "cov_html"))
cov.xml_report(outfile=str(DATA_PATH / "cov.xml"))
