#!/bin/bash

# Blog update script with retry mechanism for SSH connection issues

MAX_RETRIES=3
RETRY_DELAY=5

echo "Starting blog sync..."

for i in $(seq 1 $MAX_RETRIES); do
    echo "Attempt $i of $MAX_RETRIES"
    
    # Execute git operations
    git pull
    git add .
    git commit -m "auto update"
    git push
    
    # Check if the last command (git push) was successful
    if [ $? -eq 0 ]; then
        echo "Blog sync completed successfully on attempt $i"
        exit 0
    else
        echo "Attempt $i failed"
        if [ $i -lt $MAX_RETRIES ]; then
            echo "Waiting $RETRY_DELAY seconds before retrying..."
            sleep $RETRY_DELAY
        fi
    fi
done

echo "Blog sync failed after $MAX_RETRIES attempts"
exit 1