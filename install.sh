wget https://raw.githubusercontent.com/scriptum/hostsblock/master/hostsblock.sh && bash hostsblock.sh  install

sudo apt update  && sudo apt install -y  git curl htop nload vnstat  python3   python3-pip  iftop nethogs  mosh  net-tools fail2ban
sudo timedatectl set-timezone Asia/Tehran

pip install logzio-python-handler  
pip install -U 'logzio-python-handler[opentelemetry-logging]'

#write out current crontab
crontab -l > mycron
#echo new cron into cron file
echo "*/6  * * * * python3 /root/v2ray_manager/updater.py" >> mycron
echo "*/5  * * * * python3 /root/v2ray_manager/blocker.py" >> mycron
#install new cron file
crontab mycron
rm mycron

ufw allow 22
ufw allow 2280
ufw deny 80
ufw allow 443
ufw allow 2052
ufw allow 2053
ufw allow 2083
ufw allow 8080

ufw deny out from any to 10.0.0.0/8
ufw deny out from any to 172.16.0.0/12
ufw deny out from any to 192.168.0.0/16
ufw deny out from any to 100.64.0.0/10
ufw deny out from any to 198.18.0.0/15
ufw deny out from any to 169.254.0.0/16

ufw enable
systemctl stop nginx
systemctl disable nginx


git clone https://github.com/website-template/html5-simple-personal-website.git
mv  /usr/share/nginx/html /usr/share/nginx/html_bk
mv /usr/share/nginx/html5-simple-personal-website/ /usr/share/nginx/html

python3 /root/v2ray_manager/updater.py