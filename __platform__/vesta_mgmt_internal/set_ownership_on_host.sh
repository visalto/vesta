#!/bin/bash

# Script to set ownership and permissions for a user on all files within a fixed directory

# Fixed directory path
directory="/home/vesta"

# Check if the username argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <username>"
    exit 1
fi

# Extract the username argument
username="$1"

# Set ownership and permissions
sudo chown -R $username:$username $directory
sudo find $directory -type d -exec chmod 755 {} \;
sudo find $directory -type f -exec chmod 644 {} \;

echo "Ownership and permissions set for user $username on all files in $directory"
