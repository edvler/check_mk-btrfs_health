#!/bin/sh
mounts_btrfs=$(mount | grep btrfs | awk '{ print $3 }')

for vol in $mounts_btrfs
do
   scrub_check="btrfs scrub status $vol | grep running | wc -l"

   ionice -c 3 nice -n19 btrfs scrub start $vol

   sleep 10

   status=$(eval "$scrub_check")

   while [ $status -gt "0" ]
   do
        echo "btrfs scrub is running on $vol"
        sleep 60
        status=$(eval "$scrub_check")
   done
done
