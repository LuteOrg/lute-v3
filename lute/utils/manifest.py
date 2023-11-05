"""
Read the app manifest.
"""

import os
import yaml

def read_manifest():
    """
    Read yml file in project root.
    """
    thisdir = os.path.dirname(os.path.realpath(__file__))
    m = os.path.join(thisdir, '..', 'manifest.yml')
    if not os.path.exists(m):
        return {}
    with open(m, 'r', encoding='utf-8') as f:
        result = yaml.safe_load(f)
    return result
