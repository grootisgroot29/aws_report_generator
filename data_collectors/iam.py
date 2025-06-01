import boto3
from datetime import datetime, timezone

#IAM User data pull
def get_iam_users_with_metrics():
    try:
        iam = boto3.client('iam')
        users_response = iam.list_users()
        iam_data = []

        for user in users_response['Users']:
            username = user['UserName']
            print(f"Processing IAM user: {username}")

            try:
                #Get groups
                groups_response = iam.list_groups_for_user(UserName=username)
                groups = [g['GroupName'] for g in groups_response['Groups']]
                group_str = ', '.join(groups) if groups else 'None'

                #MFA status
                mfa_response = iam.list_mfa_devices(UserName=username)
                mfa_status = 'Enabled' if mfa_response['MFADevices'] else 'Disabled'

                #Access key age
                key_response = iam.list_access_keys(UserName=username)
                key_ages = []
                for key in key_response['AccessKeyMetadata']:
                    if key['Status'] == 'Active':
                        age_days = (datetime.now(timezone.utc) - key['CreateDate']).days
                        key_ages.append(age_days)

                active_key_age = min(key_ages) if key_ages else "No active keys"

                iam_info = {
                    'username': username,
                    'groups': group_str,
                    'mfa': mfa_status,
                    'active_key_age_(days)': active_key_age
                }

                iam_data.append(iam_info)
                print(f"Collected IAM metrics for: {username}")

            except Exception as user_error:
                print(f"Error processing user {username}: {user_error}")
                #error entry
                iam_data.append({
                    'username': username,
                    'groups': 'Error',
                    'mfa': 'Error',
                    'active_key_age_(days)': 'Error'
                })

        return iam_data

    except Exception as e:
        print(f"❌ Error getting IAM users: {str(e)}")
        return []


