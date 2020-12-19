#!/bin/bash
echo Scrap Start
cd /root/Codes/Bots/DAQ_scrap/
python3 Execute.py all

cd /root/Codes/Bots/DAQ_scrap/pages
echo Push Start
sudo git add --all
sudo git commit -m 'regular uploading of articles'
sudo git push origin master
