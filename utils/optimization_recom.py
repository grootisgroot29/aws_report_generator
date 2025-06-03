import boto3

def get_aws_optimization_status():
    client = boto3.client("compute-optimizer")

    ec2_response = client.get_ec2_instance_recommendations()
    rds_response = client.get_database_recommendations()

    categorized = {
        "Optimized": [],
        "Over Provisioned": [],
        "Under Provisioned": [],
        "No Recommendation": []
    }

    for instance in ec2_response.get("instanceRecommendations", []):
        name = instance["instanceArn"].split("/")[-1]
        status = instance["finding"]
        categorized[_map_finding(status)].append(name)

    for db in rds_response.get("recommendations", []):
        name = db["databaseArn"].split("/")[-1]
        status = db["finding"]
        categorized[_map_finding(status)].append(name)

    return categorized

def _map_finding(finding):
    mapping = {
        "OVER_PROVISIONED": "Over Provisioned",
        "UNDER_PROVISIONED": "Under Provisioned",
        "OPTIMIZED": "Optimized"
    }
    return mapping.get(finding, "No Recommendation")
