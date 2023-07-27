ufw allow 22
ufw allow 80
ufw allow 443
ufw allow 9090

sudo ufw allow from "185.126.5.177" to any comment "Pars Abr"
sudo ufw allow from "185.126.3.111" to any comment "Pars Abr"
sudo ufw allow from "185.126.3.104" to any comment "Pars Abr"
sudo ufw allow from "65.109.138.233" to any comment "hetzner"
sudo ufw allow from "65.109.1.2"     to any comment "hetzner"

sudo ufw allow from "185.140.56.136" to any comment "Office"   


ufw enable