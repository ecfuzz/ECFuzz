#!/bin/sh
#Open the coredump
ulimit -c unlimited
# echo "00000000"
# ls ~
#Clean and create coredump location
# str=$HOME"/corefile"
# echo $str
if [ -d "/home/hadoop/corefile" ];then
rm -rf /home/hadoop/corefile
# echo "11111111"
fi
# exit
# mkdir /corefile
# echo "22222222"
mkdir /home/hadoop/corefile

#Specify the location for coredump
# sudo bash -c 'echo "~/corefile/core-%e-%p-%t" > /proc/sys/kernel/core_pattern'
echo "kb310" | sudo bash -c 'echo "~/corefile/core-%e-%p-%t" > /proc/sys/kernel/core_pattern'  
