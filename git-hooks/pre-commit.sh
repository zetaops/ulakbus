#!/bin/sh
# this hook is in SCM so that it can be shared
# to install it, create a symbolic link in the projects .git/hooks folder
#
#       i.e. - from the .git/hooks directory, run
#               $ ln -s ../../git-hooks/pre-commit.sh pre-commit
#
# to skip the tests, run with the --no-verify argument
#       i.e. - $ 'git commit --no-verify'

# stash any unstaged changes
git stash -q --keep-index
ZENGINE_SETTINGS='ulakbus.settings'
PYOKO_SETTINGS='ulakbus.settings'
# run the tests
py.test

# store the last exit code in a variable
RESULT=$?

# unstash the unstashed changes
git stash pop -q

# return the py.test exit code
exit $RESULT
