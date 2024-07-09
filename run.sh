#!/bin/bash

# Function to handle errors
handle_error() {
    echo "Error: $1"
    exit 1
}

# Set trap to catch errors and call the handle_error function
trap 'handle_error "An error occurred on line $LINENO"' ERR

# go to user folder
cd /home/qianyucazelles/ || handle_error "Failed to copy scripts"

# Copy scripts
gsutil cp -r gs://chabot_backend_api . || handle_error "Failed to copy scripts"

# Go to folder
cd chabot_backend_api || handle_error "Failed to change directory"

# Run nvidia-smi and capture the output
if ! command -v nvidia-smi &> /dev/null; then
    echo "nvidia-smi command not found. Installing drivers..."
    sudo /opt/deeplearning/install-driver.sh || handle_error "Failed to install drivers"
else
    output=$(nvidia-smi 2>&1)

    # Check if nvidia-smi shows an error
    if echo "$output" | grep -q "NVIDIA-SMI has failed"; then
        echo "NVIDIA-SMI failed. Installing drivers..."
        sudo /opt/deeplearning/install-driver.sh || handle_error "Failed to install drivers"
    else
        echo "NVIDIA GPU detected. No need to install drivers."
    fi
fi


# # Install dependencies
# echo "Create venv"
# python -m venv venv || handle_error "Failed to create virtual environment"
source venv/bin/activate || handle_error "Failed to activate virtual environment"
pip install -r requirements.txt || handle_error "Failed to install Python dependencies"

# Install pm2
echo "Install pm2"
npm install -g pm2 || handle_error "Failed to install pm2"

# pm2 start application
echo "pm2 start application"
pm2 start "uvicorn main:app --host 0.0.0.0 --port 8503" --name chatbot_backend || handle_error "Failed to start application with pm2"