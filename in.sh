
sudo apt update  && sudo apt install -y  git curl htop nload vnstat  python3   python3-pip  iftop nethogs  mosh  net-tools fail2ban openvpn shadowsocks-libev  certbot 

sudo timedatectl set-timezone Asia/Tehran

bash <(curl -sSL https://raw.githubusercontent.com/hamid-gh98/x-ui-scripts/main/install_warp_proxy.sh)

pip install --break-system-packages logzio-python-handler  bpytop
pip install --break-system-packages -U 'logzio-python-handler[opentelemetry-logging]'


randTime=$[ $RANDOM % 40 + 10 ]
#write out current crontab
crontab -l > mycron
#echo new cron into cron file
echo "${randTime}  * * * * python3 /root/v2ray_panel_controller/update.py" >> mycron
echo "*/5  * * * * python3 /root/v2ray_panel_controller/blocker.py" >> mycron
#install new cron file
crontab mycron
rm mycron