import sys

from google.api_core.exceptions import NotFound
import google.auth
from google.cloud import compute_v1

from .. import (
  create,
  helpers,
  vm_config as config
)

def main():
  global config

  # Get instance name
  if len(sys.argv) != 2:
    print("Need to provide instance name")
    exit(1)

  INSTANCE_NAME = sys.argv[1]

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

  metadata_startup = [compute_v1.Items(
    key = "startup-script",
    value = config.STARTUP_SCRIPT
  )]

  instance = helpers.create_instance(project, INSTANCE_NAME, disks, metadata_startup)

  # Create firewall rule
  helpers.create_firewall_rule(project)

  # apply network tag to instance
  helpers.apply_network_tag(instance, project)
  print("Network tag set successfully")

  # Get external ip and print. Adapted from
  # https://docs.cloud.google.com/compute/docs/instances/view-network-properties
  external_ip = ""
  if not instance.network_interfaces:
    print("Instance does not have any network interfaces")
    exit(1)

  for interface in instance.network_interfaces:
    for config in interface.access_configs:
      if config.type_ == "ONE_TO_ONE_NAT":
        external_ip = config.nat_i_p

  print(
    "The Flask application is available at:\n"
   f"http://{external_ip}:5000"
  )

if __name__ == "__main__":
  main()
