import boto3
from datetime import datetime, timedelta

def get_monthly_billing_data():
    client = boto3.client('ce')
    today = datetime.today()
    start = today.replace(day=1).strftime('%Y-%m-%d')
    end = (today.replace(day=1) + timedelta(days=32)).replace(day=1).strftime('%Y-%m-%d')

    response = client.get_cost_and_usage(
        TimePeriod={'Start': start, 'End': end},
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
    )

    billing_data = {}
    for group in response['ResultsByTime'][0]['Groups']:
        service = group['Keys'][0]
        amount = float(group['Metrics']['UnblendedCost']['Amount'])
        if amount > 0:
            billing_data[service] = amount

    return billing_data
