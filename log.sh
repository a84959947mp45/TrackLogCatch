#!/bin/bash

temp_file=$(mktemp)
temp_file2=$(mktemp)
mkdir -p deepracer_log
cd deepracer_log
awslogs streams /aws/deepracer/leaderboard/SimulationJobs -s 2020-05-10T23:59:59 -e 2020-12-30T23:59:59 > $temp_file
cat $temp_file | sort -t '/' -k 2 -r | head -n $1 > $temp_file2
cat $temp_file2 | xargs -I{} sh -c 'mkdir -p "$1"; aws logs pull --log-group-name /aws/deepracer/leaderboard/SimulationJobs --log-stream-name "$1" > "$1.txt"' -- {}

