# AWS Report Generator


This tool automates the collection of AWS infrastructure metrics and generates a comprehensive PowerPoint report. It gathers data for services like EC2, RDS, EKS, IAM, and AWS Backup, visualizes performance metrics, and summarizes monthly costs.

## Features

-   **Multi-Service Data Collection**: Gathers detailed information from core AWS services:
    -   **EC2**: Instance specifications, status, and performance metrics (CPU, Memory, Disk).
    -   **RDS**: Instance details, engine versions, storage usage, and CPU utilization.
    -   **EKS**: Cluster versions, node group information, and Kubernetes support status.
    -   **IAM**: User lists, group memberships, MFA status, and active access key age.
-   **Backup & Recovery Status**: Checks for EC2 AMIs and RDS automated snapshots, reporting on backup dates, status, and retention periods.
-   **Cost Analysis**: Fetches monthly billing data from AWS Cost Explorer and visualizes spending by service.
-   **Performance Graphing**: Generates monthly time-series graphs for EC2 and RDS CPU and memory usage using Matplotlib.
-   **Optimization Insights**: Utilizes AWS Compute Optimizer to categorize EC2 and RDS instances as Optimized, Over-provisioned, or Under-provisioned.
-   **Automated Reporting**: Populates a predefined PowerPoint template (`.pptx`) with all collected data, tables, and graphs, creating a presentation-ready report.

## Project Structure

The repository is organized into modules for data collection, utility functions, and I/O.

```
aws_report_generator/
│
├── main.py                   # Main script to orchestrate data collection and report generation
├── template/
│   └── Report1.pptx          # Source PowerPoint template
├── output/
│   └── AWS_Services_Report.pptx # Generated report
│
├── data_collectors/
│   ├── ec2.py                # Collects EC2 instance and backup data
│   ├── rds.py                # Collects RDS instance and snapshot data
│   ├── eks.py                # Collects EKS cluster data
│   └── iam.py                # Collects IAM user data
│
└── utils/
    ├── cloudwatch.py         # Fetches metrics from CloudWatch
    ├── monthly_billing.py    # Fetches billing data from Cost Explorer
    ├── monthly_metric.py     # Gathers time-series data for plots
    ├── optimization_recom.py # Gets recommendations from Compute Optimizer
    ├── plots.py              # Generates metric graphs with Matplotlib
    └── ppt_edit.py           # Handles editing of the PowerPoint template
```

## Prerequisites

-   Python 3.x
-   AWS account with programmatic access.
-   Configured AWS credentials (e.g., via `~/.aws/credentials` file or environment variables) with IAM permissions for the following services:
    -   `ec2:Describe*`
    -   `rds:Describe*`
    -   `iam:List*`, `iam:Get*`
    -   `eks:List*`, `eks:Describe*`
    -   `backup:List*`, `backup:Describe*`
    -   `cloudwatch:GetMetricStatistics`
    -   `ce:GetCostAndUsage`
    -   `compute-optimizer:Get*`
    -   `sts:GetCallerIdentity`
-   For full EC2 metric coverage (memory, disk), the [CloudWatch agent](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Install-CloudWatch-Agent.html) must be installed and configured on your EC2 instances to report metrics to the `CWAgent` namespace.

## Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/grootisgroot29/aws_report_generator.git
    cd aws_report_generator
    ```

2.  **Install the required dependencies:**
    ```sh
    pip install boto3 python-pptx matplotlib
    ```

## Usage

1.  Ensure your AWS credentials are configured in your environment.

2.  Run the main script from the root of the project directory:
    ```sh
    python main.py
    ```

3.  The script will print its progress to the console as it collects data from each service.

4.  Upon completion, the final report will be saved as `output/AWS_Services_Report.pptx`. Any generated graphs will also be stored in the `output/` directory.

### Using a Custom Template

You can specify a path to your own PowerPoint template. The script identifies which slide to edit based on the title text on the slide, so ensure your custom template titles match those in the default `template/Report1.pptx`.

```sh
python main.py path/to/your/custom_template.pptx
