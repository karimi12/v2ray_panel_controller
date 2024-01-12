ufw allow 22
ufw allow 80
ufw allow 443
ufw allow 9090


sudo ufw allow from "31.214.250.152" to any comment "Pars Abr"
sudo ufw allow from "31.47.42.137" to any comment "hetzner"

sudo ufw allow from "185.140.56.136" to any comment "Office"   
sudo ufw allow from "185.124.112.229" to any comment "pal"

ufw enable