from typing import Any

import google.auth
from google.api_core.exceptions import NotFound
from google.cloud import compute_v1

from . import (
  create,
  vm_config as config
)

def create_instance(
  project: str = "",
  instance_name: str = "",
  disks: list[compute_v1.AttachedDisk] = [],
  metadata_items: list[compute_v1.Items] | None = None
) -> compute_v1.Instance:
  global config

  if metadata_items is None:
      metadata_items = []

  metadata_items.append(
    compute_v1.Items(
      key = "vmDnsSetting",
      value = "ZONAL_ONLY"
    )
  )

  return create.create_instance(
    project,
    config.ZONE,
    instance_name,
    disks,
    machine_type = config.MACHINE_TYPE,
    metadata_items = metadata_items,
    external_access = True
  )

def create_firewall_rule(
  project: str = ""
) -> None:
  firewall_client = compute_v1.FirewallsClient()
  firewall_get_request = compute_v1.GetFirewallRequest(
    project = project,
    firewall = config.NETWORK_TAG
  )

  try:
    firewall_client.get(request = firewall_get_request)
  except NotFound:
    firewall_insert_request = compute_v1.InsertFirewallRequest(
      project = project,
      firewall_resource = compute_v1.Firewall(
        name = config.NETWORK_TAG,
        source_ranges = ["0.0.0.0/0"],
        allowed = [compute_v1.Allowed(
          I_p_protocol = "tcp",
          ports = ["5000"]
        )],
        target_tags = [config.NETWORK_TAG]
      )
    )

    firewall_operation = firewall_client.insert(request = firewall_insert_request)

    create.wait_for_extended_operation(firewall_operation, "firewall rule insert")

    print("Firewall rule set successfully")
  else:
    print("Firewall rule already exists")

def apply_network_tag(
  instance: compute_v1.Instance,
  project: str = ""
) -> Any:
  global config

  instance_client = compute_v1.InstancesClient()
  tag_items = instance.tags.items

  if config.NETWORK_TAG not in tag_items:
      tag_items.append(config.NETWORK_TAG)

  tag_request = compute_v1.SetTagsInstanceRequest(
    instance = instance.name,
    project = project,
    zone = config.ZONE,
    tags_resource = compute_v1.Tags(
      fingerprint = instance.tags.fingerprint,
      items = tag_items
    )
  )

  tag_operation = instance_client.set_tags(request = tag_request)

  return create.wait_for_extended_operation(tag_operation, "Network tag set")
