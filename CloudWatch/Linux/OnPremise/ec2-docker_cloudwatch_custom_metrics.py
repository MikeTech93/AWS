import subprocess
import boto3
import requests
import re
import json

def get_aws_region():
    url = "http://169.254.169.254/latest/dynamic/instance-identity/document"

    response = requests.get(url)
    response_json = response.json()

    return response_json["region"]

def get_ec2_instance_id():
    url = "http://169.254.169.254/latest/meta-data/instance-id"

    response = requests.get(url)

    return response.text

def get_docker_container_stats():
    output = subprocess.check_output(["docker", "stats", "--no-stream", "--format", "{\"container\": \"{{ .Name }}\",\"name\": \"{{ .Name }}\", \"memory\": { \"raw\": \"{{ .MemUsage }}\", \"percent\": \"{{ .MemPerc }}\"}, \"cpu\": \"{{ .CPUPerc }}\"}"]).decode("utf-8")
    stats_list = [json.loads(line) for line in output.strip().split("\n")]

    return stats_list

def send_metrics_to_cloudwatch(container_stats, aws_region, namespace):
    cloudwatch = boto3.client("cloudwatch", region_name=aws_region)
    instance_id = get_ec2_instance_id()

    for stats in container_stats:
        container_name = stats["name"]
        cpu_perc = re.sub("%", "", stats["cpu"])
        mem_percent = re.sub("%", "", stats["memory"]["percent"])

        dimensions = [
            {"Name": "ContainerName", "Value": container_name},
            {"Name": "InstanceID", "Value": instance_id},
        ]
        cloudwatch.put_metric_data(
            Namespace=namespace,
            MetricData=[
                {
                    "MetricName": "CPUUsage",
                    "Value": float(cpu_perc),
                    "Unit": "Percent",
                    "Dimensions": dimensions,
                },
                {
                    "MetricName": "MemoryUsage",
                    "Value": float(mem_percent),
                    "Unit": "Percent",
                    "Dimensions": dimensions,
                },
            ],
        )

if __name__ == "__main__":
    cloudwatch_namespace = "EC2-Docker/ContainerMetrics" 
    aws_region = get_aws_region()
    instance_id = get_ec2_instance_id()
    container_stats = get_docker_container_stats()

    send_metrics_to_cloudwatch(container_stats, aws_region, cloudwatch_namespace)
