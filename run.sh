#!/bin/bash
echo Scrap Start
cd /root/Codes/Bots/DAQ_scrap/
python3 Execute.py all

cd /root/Codes/Bots/DAQ_scrap/pages
echo Push Start
sudo git add --all
sudo git commit -m 'regular uploading of articles'
expect <<EOF
spawn bash -c "git push origin master"
sleep 1
expect -re "Username"
send "freelunacy@gmail.com\r"
expect -re "Password"
send "make1213!\r"
expect eof
EOF
