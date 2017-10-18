# -*- coding:utf-8 -*-

import os
import re
import codecs


def find_version():
    here = os.path.abspath(os.path.dirname(__file__))
    there = os.path.join(here, 'jvirtualenv', '__main__.py')

    version_file = codecs.open(there, 'r').read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)

    else:
        raise RuntimeError("Unable to find version string.")


if __name__ == '__main__':
    print(find_version())