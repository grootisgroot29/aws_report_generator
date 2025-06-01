**AWS Infrastructure Reporting Automation Tool**

This tool automates the collection of AWS infrastructure metrics and generates a PowerPoint report with graphs and summary data for services like EC2, RDS, EKS, IAM, and backups.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**Features**

- Collects EC2 metrics: CPU, Memory, Disk usage (from CloudWatch and CWAgent)
- Collects RDS metrics: CPUUtilization, FreeStorageSpace, FreeableMemory
- Collects EKS cluster configurations
- Lists IAM users
- Checks EC2 & RDS backup/snapshot presence
- Generates monthly graphs per resource
- Populates data and visuals into a PowerPoint using a custom template

**Project Structure**

aws_report_generator/

│

├── main.py # Main entry point

├── utils/

│ ├── ec2_metrics.py #EC2 metric collection

│ ├── rds_metrics.py #RDS metric collection

│ ├── eks_info.py #EKS cluster info

│ ├── iam_info.py #IAM user info

│ ├── backup_info.py #Backup/snapshot checking

│ ├── graph_plotting.py #Monthly graph plotting (matplotlib)

│ ├── pptx_utils.py #PowerPoint editing helpers

├── template/

│ └── Report1.pptx # PowerPoint template with sample slides

│

├── output/ # Output graphs and final PPTX report

**Requirements**

boto3==1.38.17

python-pptx
