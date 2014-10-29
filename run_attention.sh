#!/bin/sh

cd /home/root/fashion-edison
echo starting loading lights
python led.py pulse_fast &
pid=$!
echo blocking bluetooth, waiting 10 sec
rfkill block 2
sleep 10
echo running init_bluetooth.sh
./init_bluetooth.sh
echo waiting 30 sec
sleep 30
kill $pid
echo starting attention.py
python attention.py
