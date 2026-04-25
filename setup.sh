#!/bin/bash

# ==========================================
# Hyprid AI CLI - Kali Linux Setup Script
# ==========================================

echo -e "\e[1;36m[*] Starting setup for Hyprid AI CLI...\e[0m"

# Removed Ollama requirements since the tool now relies entirely on OpenRouter API.

# 3. Install Python requirements
echo -e "\e[1;36m[*] Installing Python dependencies...\e[0m"
# In Kali Linux, we might need --break-system-packages to use pip natively outside venv, 
# or just install them locally
pip3 install -r requirements.txt --break-system-packages || pip3 install -r requirements.txt

# 4. Setup globally
echo -e "\e[1;36m[*] Installing 'hyprid' command to /usr/local/bin...\e[0m"
chmod +x hyprid.py
sudo cp hyprid.py /usr/local/bin/hyprid

echo -e "\e[1;32m[============== DONE ==============]\e[0m"
echo -e "Installation complete! You can now launch it by typing: \e[1;31mhyprid\e[0m"
echo -e "Example: \e[1;31mhyprid \"كيف افحص جميع المنافذ المفتوحة بالموقع x.com\"\e[0m"
