#!/bin/bash

# This is the bash script that will be run on the echo
# It will receive the value from the remote server, any of the following:
#
# - "mics-off_on"
# - "mics-off_start"
# - "mics-off_end"
# - "error"
# - "off"
# - "solid_blue"
# - "solid_cyan"
# - "solid_green"
# - "solid_orange"
# - "solid_red"
# - "solid_white
# - "zzz_disco"
# - "zzz_rainbow"
# - "zzz_turbo-boost"

HOST="http://192.168.1.81"  # Replace with the local IP of the machine running the server script.
LAST_RESPONSE=""

send_request() {
    local response
    response=$(/data/local/tmp/curl -sSL "$HOST/led")  # Capture the response output

    # Compare with the previous response
    if [[ "$response" != "$LAST_RESPONSE" ]]; then
        # Print the response body only if it's different from the last one
        ledctrl -c
        ledctrl -s $response
        LAST_RESPONSE="$response"  # Update the last response
    fi

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
            sleep 30
        fi
    done
}

while true; do
    send_request
    status_code=$?

    if [[ $status_code -ne 0 ]]; then
        echo "Request failed. Retrying..."
        handle_unsuccessful_req
    fi
    sleep 5
done