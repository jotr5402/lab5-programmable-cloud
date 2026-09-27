ZONE = "us-west1-a" 
DISK_TYPE = f"zones/{ZONE}/diskTypes/pd-standard"
MACHINE_TYPE = f"zones/{ZONE}/machineTypes/f1-micro"

IMAGE_PROJECT = "ubuntu-os-cloud"
IMAGE_FAMILY =  "ubuntu-2204-lts"

STARTUP_SCRIPT = (
"""
#!/bin/sh

sudo apt-get update
sudo apt-get install -y python3 python3-pip git

git clone https://github.com/cu-csci-4253-datacenter/flask-tutorial

cd flask-tutorial

sudo python3 setup.py install
sudo pip3 install -e .

export FLASK_APP=flaskr
flask init-db
nohup flask run -h 0.0.0.0 &
"""
)

NETWORK_TAG = "allow-5000"
