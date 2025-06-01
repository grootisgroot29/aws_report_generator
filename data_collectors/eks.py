import boto3


def get_kubernetes_support_period(version):
    version_support = {
        '1.31': 'Until Feb 2026',
        '1.30': 'Until Nov 2025',
        '1.29': 'Until Aug 2025',
        '1.28': 'Until May 2025',
        '1.27': 'Until Feb 2025',
        '1.26': 'Expired Nov 2024',
        '1.25': 'Expired Aug 2024',
        '1.24': 'Expired May 2024',
    }
    return version_support.get(version, "Unknown/Expired")


#EKS Cluster data pull
def get_eks_clusters_with_metrics():
    try:
        eks = boto3.client('eks')
        print("Fetching EKS clusters...")

        cluster_names_response = eks.list_clusters()
        cluster_names = cluster_names_response.get('clusters', [])

        if not cluster_names:
            print("No EKS clusters found")
            return []

        eks_data = []

        for name in cluster_names:
            try:
                print(f"Processing EKS cluster: {name}")

                desc_response = eks.describe_cluster(name=name)
                desc = desc_response['cluster']

                version = desc['version']
                status = desc['status']
                support_period = get_kubernetes_support_period(version)

                #Get node groups
                try:
                    nodegroup_response = eks.list_nodegroups(clusterName=name)
                    nodegroup_names = nodegroup_response.get('node_groups', [])
                    node_groups_str = ', '.join(nodegroup_names) if nodegroup_names else 'None'
                except Exception as ng_error:
                    print(f"Error fetching node groups for {name}: {ng_error}")
                    node_groups_str = 'Error fetching'

                eks_info = {
                    'cluster_name': name,
                    'kubernetes_version': version,
                    'support_period': support_period,
                    'node_groups': node_groups_str,
                    'status': status
                }

                print(f"Collected EKS info for: {name}")
                eks_data.append(eks_info)

            except Exception as cluster_error:
                print(f"Error fetching EKS cluster {name}: {cluster_error}")
                # error entry
                eks_data.append({
                    'cluster_name': name,
                    'kubernetes_version': 'Error',
                    'support_period': 'Error',
                    'node_groups': 'Error',
                    'status': 'Error'
                })

        return eks_data

    except Exception as e:
        print(f"Error accessing EKS service: {str(e)}")
        print("   This might be due to:")
        print("   - EKS service not available in this region")
        print("   - Insufficient IAM permissions")
        print("   - EKS service not enabled")
        return []