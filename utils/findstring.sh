# set -e
# set -x

args=("$@")
if [[ "$#" -eq "0" ]]; then
    echo "Need search string."
fi;
echo "Searching for $@ :"
echo

SEARCHFOR="$@"

function runsearch() {
    echo "# $1 ---------------"
    find $1 -name "*.*" -maxdepth $2 -print0 | xargs -0 grep "$SEARCHFOR" 2>/dev/null | grep -v findstring.sh | grep -v Binary | grep -v js/jquery | grep -v docs/archive | grep -v lute/static/vendor
}

runsearch . 1
runsearch lute 8
runsearch tests 8
runsearch utils 8
runsearch .github 8

# Script sometimes returned w/ non-zero exit code,
# breaking testing.
exit 0
