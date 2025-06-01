
import boto3
from datetime import datetime, timedelta, timezone


#CloudWatch metric
#    Parameters:
#     - instance_id (str): ID of the instance or resource (e.g., EC2, RDS)
#     - metric_name (str): Name of the CloudWatch metric
#     - namespace (str): Namespace of the metric (default: 'CWAgent')
#     - stat (str): Statistic to retrieve (e.g., 'Average', 'Maximum')
#     - dimension_name (str): Dimension key to use (default: 'InstanceId')
#
#     Returns:
#     - float or str: The metric value or "N/A"/"Error"

def get_cloudwatch_metric(instance_id, metric_name, namespace='CWAgent', stat='Average', dimension_name='InstanceId'):

    try:
        session = boto3.Session()
        cloudwatch = session.client('cloudwatch')

        now = datetime.now(timezone.utc)
        print(f"Fetching {metric_name} for {instance_id} from namespace {namespace}")

        response = cloudwatch.get_metric_statistics(
            Namespace=namespace,
            MetricName=metric_name,
            Dimensions=[{'Name': dimension_name, 'Value': instance_id}],
            StartTime=now - timedelta(hours=24),
            EndTime=now,
            Period=3600,
            Statistics=[stat]
        )

        datapoints = response.get('Datapoints', [])
        if datapoints:
            datapoints.sort(key=lambda x: x['Timestamp'], reverse=True)
            value = round(datapoints[0][stat], 2)
            print(f"Got {metric_name}: {value}")
            return value
        else:
            print(f"No datapoints found for {metric_name}")
            return "N/A"

    except Exception as e:
        print(f"Error fetching {metric_name} for {instance_id}: {str(e)}")
        return "Error"
