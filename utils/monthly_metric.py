import boto3
from datetime import datetime, timedelta, timezone

def get_monthly_metrics(resource_id, metric_names, namespace, dimension_name):
    cloudwatch = boto3.client('cloudwatch')
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=30)
    metrics_data = {}

    for metric in metric_names:
        try:
            response = cloudwatch.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric,
                Dimensions=[{'Name': dimension_name, 'Value': resource_id}],
                StartTime=start,
                EndTime=now,
                Period=86400,  # Daily datapoints
                Statistics=['Average']
            )
            datapoints = response['Datapoints']
            if not datapoints:
                return None  # Skip if any metric is missing
            sorted_data = sorted([(dp['Timestamp'], dp['Average']) for dp in datapoints])
            metrics_data[metric] = sorted_data
        except Exception:
            return None
    return metrics_data
