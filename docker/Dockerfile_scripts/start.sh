#!/bin/sh
#
# Check that the folders given in the
# lute/config/config.yml.docker are in fact mounted.

for d in /lute_data /lute_backup; do
    checkdir=`mount | grep "$d"`
    if [ -z "$checkdir" ]
    then
        echo ""
        echo "-------------------------------------------------------"
        echo "$d container directory is not mounted, quitting."
        echo ""
        echo "Lute (containerized) writes to /lute_data and lute_backup."
        echo "BOTH of these must be mounted."
        echo ""
        echo "If these folders are not mounted from host directories,"
        echo "then the writes will go to the container's writable layer,"
        echo "and would be destroyed if the container were deleted."
        echo "That would mean loss of data, so this check prevents it."
        echo ""
        echo "Please ensure you mount a host directory,"
        echo "either in your docker-compose.yml or in your docker run."
        echo "-------------------------------------------------------"
        echo ""
        exit
    fi
done

python -m lute.main
