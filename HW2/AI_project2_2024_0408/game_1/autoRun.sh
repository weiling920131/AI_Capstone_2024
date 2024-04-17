#!/bin/bash
for i in {1..50}; do
    touch "record.txt"
    echo "执行第 $i 次操作"
    ./AI_game.exe >> record.txt &
    pid=$!
    echo "pid: $pid"
    sleep 20
    kill -9 $pid
    break
done
