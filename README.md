# Smart Cloud Official Tip bot

## Instructions

These instructions were used to create a working bot in September 2018. Once a VPS is obtained, follow these instructions.

### mySQL

These instructions will help you install and setup a mySQL database
### Install mySQL

sudo apt-get install mysql-server

When prompted, set up a password for root.

### Configure mySQL Security

mysql_secure_installation

Press "Y" and ENTER to accept all the questions, with the exception of the one that asks if you'd like to change the root password.

### Verify mySQL is Running

systemctl status mysql.service

You should see a status message that says "active (running)".

### Update Python

Python should be updated to version 3.6 because version 3.5 is not compatible with some libraries

sudo add-apt-repository ppa:jonathonf/python-3.6
sudo apt update
sudo apt-get install python3.6
sudo apt-get install python3.6-dev
sudo apt-get install python3.6-venv

### Install Python's pip

Python's pip is a useful tool used to install python libraries

wget https://bootstrap.pypa.io/get-pip.py
sudo python3.6 get-pip.py

### Link python3 to python3.6

sudo ln -s /usr/bin/python3.6 /usr/local/bin/python3

### Install Discord Library

Install the discord library used for the bot

python3 -m pip install -U discord.py

### Install PyMySQL Library

pip install PyMySQL






Special thanks goes to Curium Discord-Curium-Tips
[Curium Discord](https://discord.gg/BNxtX7b)


