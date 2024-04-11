"""
Language file verification tests.

These are spot-check sanity checks only.  Ideally the tests would
verify that the language definition files are in fact **complete**,
i.e. contain all the necessary fields, but for now this will suffice.
Lute will double-check that the files are valid anyway.
"""

import unittest
import re
from glob import glob
import os
import yaml


class TestVerifyFiles(unittest.TestCase):
    "Verify files."

    def test_definition_files_are_valid_yaml(self):
        "Files must be valid yaml."
        thisdir = os.path.dirname(__file__)
        langglob = os.path.join(thisdir, "**", "definition.yaml")
        for filename in glob(langglob):
            print(filename)
            with open(filename, "r", encoding="utf-8") as f:
                try:
                    d = yaml.safe_load(f)
                except Exception as e:  # pylint: disable=broad-exception-caught
                    self.fail(f"ERROR: {filename} invalid: {e}")
                self.assertTrue(d["name"] is not None, f"{filename} missing name")

    def test_story_files_contain_title(self):
        "Must have # title: at the top."
        thisdir = os.path.dirname(__file__)
        storyglob = os.path.join(thisdir, "**", "*.txt")
        for filename in glob(storyglob):
            print(filename)
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
            retitle = r"title:\s*(.*)\n"
            t = re.search(retitle, content)
            msg = f"{filename} missing '# title:' comment, {retitle}"
            self.assertTrue(t is not None, msg)
            title = t.group(1).strip()
            self.assertTrue(title != "", f"{filename} missing title")


if __name__ == "__main__":
    unittest.main()
