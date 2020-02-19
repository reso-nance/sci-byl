#!/bin/bash
#
#  Copyright 2020 Reso-nance Numérique <laurent@reso-nance.org>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
# This script install dependancies for the markov text generator

thisScriptDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

echo "
------------installing dependencies :------------
"
echo "
updating the system :"
sudo apt-get update||exit 1
sudo apt-get -y dist-upgrade||exit 1
echo "
installing .deb packages :"
sudo apt-get -y --fix-missing install python3-pip python3-dev python3-rpi.gpio \
libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev libatlas-base-dev sox ||exit 1
echo "
installing pip packages :"
pip3 install markovify||exit 2
echo "  enlarging swap to 1024Mo to compile spacy.." # this will be really long
sed -i -e 's/CONF_SWAPSIZE=100/CONF_SWAPSIZE=1024/g' /etc/dphys-swapfile||exit 2
/etc/init.d/dphys-swapfile stop && /etc/init.d/dphys-swapfile start||exit 2
pip3 install spacy==2.0.18||exit 2 # newer versions depends on blis which is currently broken for ARM plateforms
echo "  reverting to default 100Mo swap..."
sed -i -e 's/CONF_SWAPSIZE=1024/CONF_SWAPSIZE=100/g' /etc/dphys-swapfile||exit 2
/etc/init.d/dphys-swapfile stop && /etc/init.d/dphys-swapfile start||exit 2
pip3 install Cython||exit 2
pip3 install numpy ||exit 2
pip3 install pyaudio ||exit 2
python3 -m spacy download fr_core_news_sm||exit 2

echo "
adding Debian non-free repository"
wget -q https://ftp-master.debian.org/keys/release-10.asc -O- | sudo apt-key add -
echo "deb http://deb.debian.org/debian buster non-free" | sudo tee -a /etc/apt/sources.list
sudo apt-get update
echo "
installing picoTTS"
sudo apt-get install -y --fix-missing libttspico-utils


echo "
------------DONE installing dependencies------------

"

echo"
--------- setting up the wifi country as FR---------"
sudo raspi-config nonint do_wifi_country FR

echo "
--------------setting up script autolaunch:--------------
"
echo"
su pi -c 'cd /home/pi/sci-byl && python3 main.py&'
">>/etc/rc.local

# echo "
# ----------- setting up the access point ------------
# "
# chmod +x STAtoAP
# sudo ./STAtoAP

# echo "

# ----------------------------------------------------
# ----------- DONE, rebooting in 3, 2, 1... ----------
# ----------------------------------------------------"
# sleep(3); sudo reboot
