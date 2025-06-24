#!/bin/bash

# Update packages and install basic tools
apt update
apt install -y wget unzip curl

# Download and install Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y ./google-chrome-stable_current_amd64.deb

# Get Chrome version installed
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')

# Find matching ChromeDriver version
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")

# Download and install ChromeDriver
wget "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip
mv chromedriver /usr/bin/chromedriver
chmod +x /usr/bin/chromedriver

# Start your Python script
python3 main.py
