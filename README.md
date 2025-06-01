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

├── data collectors/

│ ├── ec2.py #EC2 and backup metric collection

│ ├── rds.py #RDS and backup metric collection

│ ├── eks.py #EKS cluster info

│ ├── iam.py #IAM user info

├── utils/

│ ├──plots.py #Monthly graph plotting (matplotlib)

│ ├── ppt_edit.py #PowerPoint editing helpers

├── template/

│ └── Report1.pptx # PowerPoint template with sample slides

│

├── output/ # Output graphs and final PPTX report

**Requirements**

boto3==1.38.17

python-pptx
