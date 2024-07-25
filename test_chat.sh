#!/bin/bash

# Define the URL and payload
session_url="http://0.0.0.0:8503/new_session"
chat_url="http://0.0.0.0:8503/chat"
payload='{"user_id": "123"}'

# Send the second POST request
session_id=$(curl -s -X POST -H "Content-Type: application/json" -d "$payload" "$session_url" | jq -r '.')
echo $session_id

# Send chat request
# Define the payload for the second POST request
payload_chat=$(jq -n --arg user_id "123" --arg session_id "$session_id" --arg message "tell me a joke" \
                '{user_id: $user_id, session_id: $session_id, message: $message}')

# Send the second POST request
response=$(curl -s -X POST -H "Content-Type: application/json" -d "$payload_chat" "$chat_url")

echo $response
