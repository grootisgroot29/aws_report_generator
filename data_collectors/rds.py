from utils.cloudwatch import get_cloudwatch_metric
from datetime import datetime, timezone
import boto3

#RDS Data pull
def get_rds_instances_with_metrics():
    try:
        rds = boto3.client('rds')
        response = rds.describe_db_instances()
        rds_data = []

        for db in response['DBInstances']:
            #Skip instances that are not available
            if db['DBInstanceStatus'] not in ['available', 'backing-up', 'modifying']:
                continue

            db_id = db['DBInstanceIdentifier']
            allocated_storage = db['AllocatedStorage']

            print(f"Processing RDS instance: {db_id}")

            cpu = get_cloudwatch_metric(db_id, 'CPUUtilization', namespace='AWS/RDS',
                                        dimension_name='DBInstanceIdentifier')
            free_storage = get_cloudwatch_metric(db_id, 'FreeStorageSpace', namespace='AWS/RDS',
                                                 dimension_name='DBInstanceIdentifier')

            #Calculate storage usage
            if free_storage not in ["N/A", "Error"]:
                free_storage_gb = round(free_storage / (1024 ** 3), 2)
                used_storage_gb = round(allocated_storage - free_storage_gb, 2)
                used_storage_str = f"{used_storage_gb} GB / {allocated_storage} GB"
            else:
                used_storage_str = f"N/A / {allocated_storage} GB"

            rds_info = {
                'db_identifier': db_id,
                'database_name': db.get('DBName', 'N/A'),
                'engine': f"{db['Engine']} {db.get('EngineVersion', '')}".strip(),
                'status': db['DBInstanceStatus'],
                'storage_used/allocated': used_storage_str,
                'monthly_cpu_usage_(%)': f"{cpu}%" if cpu not in ["N/A", "Error"] else cpu,
            }

            print(f"Collected RDS metrics for: {db_id}")
            rds_data.append(rds_info)

        return rds_data

    except Exception as e:
        print(f"Error getting RDS instances: {str(e)}")
        return []

def get_rds_backup_metrics():
    try:
        rds = boto3.client('rds')
        print("Fetching RDS backup information...")

        # Get all RDS instances first
        instances_response = rds.describe_db_instances()
        instances = instances_response.get('DBInstances', [])

        if not instances:
            print("No RDS instances found")
            return []

        backup_data = []

        for instance in instances:
            db_name = instance['DBInstanceIdentifier']
            print(f"Checking backups for RDS: {db_name}")

            try:
                #Get automated snapshots for specific DB instance
                snapshots_response = rds.describe_db_snapshots(
                    DBInstanceIdentifier=db_name,
                    SnapshotType='automated',
                    MaxRecords=20
                )
                snapshots = snapshots_response.get('DBSnapshots', [])

                if snapshots:
                    #Get the most recent snapshot
                    snapshots.sort(key=lambda x: x.get('SnapshotCreateTime', datetime.min.replace(tzinfo=timezone.utc)),
                                   reverse=True)
                    snapshot = snapshots[0]

                    snapshot_id = snapshot.get('DBSnapshotIdentifier', 'N/A')
                    snapshot_date = snapshot.get('SnapshotCreateTime', 'N/A')
                    snapshot_status = snapshot.get('Status', 'N/A')
                    size_gb = snapshot.get('AllocatedStorage', 0)

                    #Format date
                    if snapshot_date != 'N/A':
                        date_str = snapshot_date.strftime("%Y-%m-%d %H:%M")
                    else:
                        date_str = 'N/A'

                    print(f"Found snapshot: {snapshot_id} from {date_str}")
                else:
                    snapshot_id = "No snapshots"
                    date_str = "N/A"
                    snapshot_status = "No automated backups"
                    size_gb = 0
                    print(f"No automated snapshots found for {db_name}")

                #Get retention period from instance settings
                retention = instance.get('BackupRetentionPeriod', 0)
                retention_str = f"{retention} days" if retention > 0 else "Disabled"

                backup_data.append({
                    'db_name': db_name,
                    'snapshot_id': snapshot_id,
                    'date': date_str,
                    'status': snapshot_status,
                    'retention_days': retention_str,
                    'size_gb': f"{size_gb} GB" if size_gb > 0 else "N/A"
                })

                print(f"Collected backup info for RDS: {db_name}")

            except Exception as db_error:
                print(f"Error processing RDS backups for {db_name}: {db_error}")
                backup_data.append({
                    'db_name': db_name,
                    'snapshot_id': 'Error',
                    'date': 'Error',
                    'status': 'Error',
                    'retention_days': 'Error',
                    'size_gb': 'Error'
                })

        return backup_data

    except Exception as e:
        print(f"Error getting RDS backup metrics: {str(e)}")
        return []