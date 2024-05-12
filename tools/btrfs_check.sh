#!/bin/sh
export LC_ALL=C

mounts_btrfs=""
devices_btrfs="$(awk '/ btrfs / { print $1 }' < /proc/mounts | sort | uniq)"

for dev in $devices_btrfs; do
    mounts_btrfs="${mounts_btrfs} "$(awk "\$1 == \"${dev}\" { print \$2; exit }" < /proc/mounts)
done

mounts_btrfs=${mounts_btrfs# }

test -z $mounts_btrfs && exit


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
