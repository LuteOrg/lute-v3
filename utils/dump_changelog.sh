#!/bin/bash
#
# Prepend changelog commits since a particular commit.
#
# Usage:
#
# Dump changes from x to y:
# ./utils/dump_changelog.sh X Y
#
# Dump changes from X to _now_, reading current version.
# ./utils/dump_changelog.sh X
#
# Sample:
# ./utils/dump_changelog.sh 3.0.0b1 3.0.0b2

set -e

FROMTAG=$1
TOTAG=$2
TOCOMMIT=$2

if [[ "$FROMTAG" == "" ]]; then
    echo
    echo "Please specify the starting commit or tag."
    echo
    exit 1
fi

if [[ "$TOTAG" == "" ]]; then
    echo "Using HEAD as current version, reading the version tag."
    # Read version from python (throws if missing).
    TOTAG=$(python -c "import lute; print(lute.__version__)")
    TOCOMMIT=HEAD
fi

if [ -z "$TOTAG" ]; then
    echo
    echo "No version tag?  TOTAG is blank.  Quitting"
    echo
    exit 1
fi

if [[ "$TOTAG" == *"dev"* ]]; then
   echo "Version STILL HAS dev, please fix"
   exit 1
else
   echo "Version ${TOTAG}"
fi

if [[ "$FROMTAG" == "$TOTAG" ]]; then
    echo
    echo "Same start and end tag $FROMTAG."
    echo
    exit 1
fi

TOCOMMITDATE=$(git log --pretty=format:"%ad" --date=format:'%Y-%m-%d' -n 1 $TOCOMMIT)

# Start changelog entry.
echo "
# $TOTAG ($TOCOMMITDATE)

Feature changes:

---

_(raw info to process)_
" > docs/tmp_CHANGELOG.tmp

# Add raw log info.
git log ${FROMTAG}..${TOCOMMIT} --oneline --graph >> docs/tmp_CHANGELOG.tmp

# Finish changelog entry.
echo "

_(end raw)_
---

Back end changes:


" >> docs/tmp_CHANGELOG.tmp


# Append previous, and replace.
cat docs/CHANGELOG.md >> docs/tmp_CHANGELOG.tmp
mv docs/tmp_CHANGELOG.tmp docs/CHANGELOG.md
