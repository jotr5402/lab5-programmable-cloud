#!/usr/bin/env python3

import os
from pathlib import Path

import google.auth
from google.cloud import compute_v1

from .. import (
  create,
  helpers,
  vm_config as config
)

VM1_INSTANCE_NAME = "lab5-p3-vm1"
VM1_STARTUP = (
"""
#!/bin/sh

sudo apt-get update
sudo apt-get install -y python3 python3-pip

mkdir -p /srv/lab5
cd /srv/lab5
curl http://metadata/computeMetadata/v1/instance/attributes/create -H "Metadata-Flavor: Google" > create.py
curl http://metadata/computeMetadata/v1/instance/attributes/helpers -H "Metadata-Flavor: Google" > helpers.py
curl http://metadata/computeMetadata/v1/instance/attributes/vm-config -H "Metadata-Flavor: Google" > vm_config.py
curl http://metadata/computeMetadata/v1/instance/attributes/service-credentials -H "Metadata-Flavor: Google" > service-credentials.json
touch __init__.py

mkdir -p part3
curl http://metadata/computeMetadata/v1/instance/attributes/vm1 -H "Metadata-Flavor: Google" > part3/vm1.py
touch part3/__init__.py

cd /srv
pip3 install --upgrade google-auth google-cloud-compute
GOOGLE_APPLICATION_CREDENTIALS=lab5/service-credentials.json python3 -m lab5.part3.vm1 lab5-p3-vm2
"""
)

def main():
  global config

  os.chdir(Path(__file__).resolve().parent)

  # Get credentials
  _, project = google.auth.default()
  if project is None:
    project = ""

  # Create instance
  image = create.get_image_from_family(
    project = config.IMAGE_PROJECT, family = config.IMAGE_FAMILY
  )

  disks = [create.disk_from_image(
    config.DISK_TYPE,
    10,
    True,
    image.self_link
  )]

  metadata_items = [
    compute_v1.Items(
      key = "startup-script",
      value = VM1_STARTUP
    ),
    compute_v1.Items(
      key = "vm1",
      value = Path("../part1/part1.py").read_text(encoding = "utf-8")
    ),
    compute_v1.Items(
      key = "service-credentials",
      value = Path("service-credentials.json").read_text(encoding = "utf-8")
    ),
    compute_v1.Items(
      key = "create",
      value = Path("../create.py").read_text(encoding = "utf-8")
    ),
    compute_v1.Items(
      key = "helpers",
      value = Path("../helpers.py").read_text(encoding = "utf-8")
    ),
    compute_v1.Items(
      key = "vm-config",
      value = Path("../vm_config.py").read_text(encoding = "utf-8")
    ),
  ]

  helpers.create_instance(project, VM1_INSTANCE_NAME, disks, metadata_items)

if __name__ == "__main__":
  main()
