import time
import uuid

import google.auth
from google.cloud import compute_v1

from .. import (
  create,
  helpers,
  vm_config as config
)

def create_snapshot(
  project: str = "",
  disk_name: str = "",
  instance_name: str = "",
) -> compute_v1.Snapshot:
  # Adapated from
  # https://docs.cloud.google.com/compute/docs/samples/compute-snapshot-create
  disk_client = compute_v1.DisksClient()
  disk = disk_client.get(
    project = project,
    zone = config.ZONE,
    disk = disk_name
  )

  snapshot_client = compute_v1.SnapshotsClient()
  snapshot_name = f"base-snapshot-{instance_name}"
  snapshot_operation = snapshot_client.insert(
    project = project,
    snapshot_resource = compute_v1.Snapshot(
      source_disk = disk.self_link,
      name = snapshot_name
    )
  )

  print(f"Creating snapshot {snapshot_name}...")

  create.wait_for_extended_operation(snapshot_operation, "Snapshot creation")

  print("Snapshot created successfully")

  return snapshot_client.get(
    project = project,
    snapshot = snapshot_name
  )

def main():
  global config

  # Get instance
  _, project = google.auth.default()
  if project is None:
    project = ""

  instance_client = compute_v1.InstancesClient()
  instance_list_request = compute_v1.ListInstancesRequest(
    project = project,
    zone = config.ZONE
  )

  instance_list = instance_client.list(request = instance_list_request)

  instance_name = "lab5-p1"
  instance_found = False

  for instance in instance_list:
    if instance.name == instance_name:
      instance_found = True
      break

  if not instance_found:
    print("Could not find lab5 part 1 instance")
    exit(1)

  # Create snapshot
  snapshot = create_snapshot(project, instance_name, instance_name)
  # snapshot_client = compute_v1.SnapshotsClient()
  # snapshot_name = f"base-snapshot-{instance_name}"
  # snapshot = snapshot_client.get(
  #   project = project,
  #   snapshot = snapshot_name
  # )

  # Create 3 instances from snapshot
  disk_params = compute_v1.AttachedDiskInitializeParams(
    source_snapshot = snapshot.self_link,
    disk_type = config.DISK_TYPE
  )

  disks_new = [compute_v1.AttachedDisk(
    initialize_params = disk_params,
    auto_delete = True,
    boot = True,
  )]

  times = []
  for _ in range(3):
    instance_new_name = "lab5-from-snapshot-" + uuid.uuid4().hex[:10]

    metadata_startup = [compute_v1.Items(
      key = "startup-script",
      value = config.STARTUP_SCRIPT
    )]

    start_time = time.time()
    instance_new = helpers.create_instance(project, instance_new_name, disks_new, metadata_startup)
    helpers.apply_network_tag(instance_new, project)
    times.append(time.time() - start_time)

  print(times)

if __name__ == "__main__":
  main()
