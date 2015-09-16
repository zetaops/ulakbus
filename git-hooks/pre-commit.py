#!/usr/bin/env python

"""
Git pre-commit hook to enforce PEP8 rules and run unit tests.

Copyright (C) Sarah Mount, 2013.
https://gist.github.com/snim2/6444684#file-pre-commit-py

# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
"""

import os
import re
import subprocess
import sys

os.environ['PYOKO_SETTINGS'] = 'ulakbus.settings'
os.environ['ZENGINE_SETTINGS'] = 'ulakbus.settings'
modified_re = re.compile(r'^[AM]+\s+(?P<name>.*\.py)', re.MULTILINE)


def get_staged_files():
    """Get all files staged for the current commit.
    """
    proc = subprocess.Popen(('git', 'status', '--porcelain'),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, _ = proc.communicate()
    staged_files = modified_re.findall(out)
    return staged_files


def main():
    abort = False
    # Stash un-staged changes.
    subprocess.call(('git', 'stash', '-u', '--keep-index'),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, )
    # Determine all files staged for commit.
    staged_files = get_staged_files()
    # Enforce PEP8 conformance.

    # DISABLED pep8ify, failed at my first attempt to comply with pep8 command
    # PyCharm already doing a good job at this
    # esat
    # print('============ Enforcing PEP8 rules =============')
    # for filename in staged_files:
    #     subprocess.call(('pep8ify', '-w', filename))
    #     try:
    #         os.unlink(filename + '.bak')
    #     except OSError:
    #         pass
    #     subprocess.call(('git', 'add', '-u', 'filename'))

    print('========== Checking PEP8 conformance ==========')
    for filename in staged_files:
        proc = subprocess.Popen(('pep8', '--max-line-length', '99', filename),
                                stdout=subprocess.PIPE)
        output, _ = proc.communicate()
        # If pep8 still reports problems then abort this commit.
        if output:
            abort = True
            print()
            print('========= Found PEP8 non-conformance ==========')
            print(output)
            sys.exit(1)
            return
    # Run unit tests.

    print('============== Running unit tests =============')

    proc = subprocess.Popen(['py.test', ],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out, _ = proc.communicate()
    print(out)
    if 'FAILURES' in out:
        abort = True
    # Un-stash un-staged changes.
    subprocess.call(('git', 'stash', 'pop', '-q'),
                    stdout=subprocess.PIPE)
    # Should we abort this commit?
    if abort:
        print()
        print('=============== ABORTING commit ===============')
        sys.exit(1)
    else:
        sys.exit(0)
    return


if __name__ == '__main__':
    main()
