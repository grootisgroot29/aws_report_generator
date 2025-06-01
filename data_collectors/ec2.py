from utils.cloudwatch import get_cloudwatch_metric
import boto3

#EC2 Instances data pull
def get_ec2_instances_with_metrics():
    try:
        ec2 = boto3.client('ec2')
        response = ec2.describe_instances()
        instances = []

        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                #Skip terminated instances
                if instance['State']['Name'] in ['terminated', 'shutting-down']:
                    continue

                instance_id = instance['InstanceId']

                #Get instance name from tags
                tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                instance_name = tags.get('Name', instance_id)

                print(f"Processing instance: {instance_name} ({instance_id})")

                #Get metrics(cloudwatch and CWAgent)
                cpu = get_cloudwatch_metric(instance_id, 'CPUUtilization', namespace='AWS/EC2',
                                            dimension_name='InstanceId')
                memory = get_cloudwatch_metric(instance_id, 'mem_used_percent', namespace='CWAgent',
                                               dimension_name='InstanceId')
                disk = get_cloudwatch_metric(instance_id, 'disk_used_percent', namespace='CWAgent',
                                             dimension_name='InstanceId')

                instance_info = {
                    'instance_id': instance_id,
                    'server_name': instance_name,
                    'specification': instance['InstanceType'],
                    'status': instance['State']['Name'],
                    'monthly_cpu_usage_(%)': f"{cpu}%" if cpu not in ["N/A", "Error"] else cpu,
                    'monthly_memory_usage_(%)': f"{memory}%" if memory not in ["N/A", "Error"] else memory,
                    'monthly_disk_usage_(%)': f"{disk}%" if disk not in ["N/A", "Error"] else disk,
                }

                print(f"Collected metrics for: {instance_name}")
                instances.append(instance_info)

        return instances

    except Exception as e:
        print(f"Error getting EC2 instances: {str(e)}")
        return []

#EC2 backup metrics
def get_ec2_backup_metrics():
    try:
        ec2 = boto3.client('ec2')
        backup = boto3.client('backup')
        sts = boto3.client('sts')

        #Get account info
        account_id = sts.get_caller_identity()['Account']
        region = boto3.Session().region_name

        ec2_instances = ec2.describe_instances()
        instance_backups = []

        for reservation in ec2_instances['Reservations']:
            for instance in reservation['Instances']:
                if instance['State']['Name'] in ['terminated', 'shutting-down']:
                    continue

                instance_id = instance['InstanceId']
                ami_id = instance.get('ImageId', 'N/A')
                tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                instance_name = tags.get('Name', instance_id)

                print(f"Checking backups for: {instance_name} ({instance_id})")

                try:
                    #Construct the resource ARN
                    resource_arn = f"arn:aws:ec2:{region}:{account_id}:instance/{instance_id}"

                    #Fetch backup jobs for this instance
                    backup_jobs_response = backup.list_backup_jobs(
                        ByResourceArn=resource_arn,
                        MaxResults=5
                    )
                    backup_jobs = backup_jobs_response.get('BackupJobs', [])

                    if backup_jobs:
                        #Get the most recent successful backup
                        successful_jobs = [job for job in backup_jobs if job['State'] == 'COMPLETED']
                        if successful_jobs:
                            job = successful_jobs[0]  # Most recent successful
                            date = job['CreationDate'].strftime("%Y-%m-%d %H:%M:%S")
                            status = job['State']
                        else:
                            job = backup_jobs[0]  # Most recent regardless of status
                            date = job['CreationDate'].strftime("%Y-%m-%d %H:%M:%S")
                            status = job['State']

                        #get retention period
                        try:
                            recovery_point = backup.describe_recovery_point(
                                BackupVaultName=job['BackupVaultName'],
                                RecoveryPointArn=job['RecoveryPointArn']
                            )
                            lifecycle = recovery_point.get('CalculatedLifecycle', {})
                            retention_period = lifecycle.get('DeleteAfterDays', 'N/A')
                        except Exception:
                            retention_period = 'N/A'

                        next_backup = "Per backup plan schedule"
                    else:
                        date = "No backups found"
                        status = "No Backup"
                        retention_period = "N/A"
                        next_backup = "N/A"

                except Exception as backup_error:
                    print(f"    ⚠️ Error checking backups for {instance_id}: {backup_error}")
                    date = "Error"
                    status = "Error"
                    retention_period = "Error"
                    next_backup = "Error"

                instance_backups.append({
                    'instance_name': instance_name,
                    'ami_id': ami_id,
                    'backup_date': date,
                    'status': status,
                    'retention_days': retention_period,
                    'next_backup': next_backup
                })

        return instance_backups

    except Exception as e:
        print(f"❌ Error getting EC2 backup metrics: {str(e)}")
        return []
