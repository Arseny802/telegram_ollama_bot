#!/bin/bash
service_path=/lib/systemd/system/telegram_ollama_bot.service
current_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
current_dir=${current_dir/lin}

sudo systemctl disable telegram_ollama_bot.service
sudo systemctl stop telegram_ollama_bot.service

if [ ! -d "/var/log/arseny802/" ]; then 
  sudo mkdir /var/log/arseny802/ 
fi
if [ ! -d "/var/log/arseny802/telegram_ollama_bot_service" ]; then 
  sudo mkdir /var/log/arseny802/telegram_ollama_bot_service/
fi
sudo cp ${current_dir}/lin/telegram_ollama_bot.service $service_path

sudo sed -i "s|REPLACE_ME_WITH_PWD|${current_dir}|g" $service_path
sudo sed -i "s|REPLACE_ME_WITH_LOG_DIR|/var/log/arseny802/telegram_ollama_bot_service/|g" $service_path

sudo systemctl enable telegram_ollama_bot.service
sudo systemctl start telegram_ollama_bot.service
