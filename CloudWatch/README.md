# How to set custom metrics configuration (Linux & Windows)
```bash
# Check CloudWatch agent is installed
    # Windows
        cd 'C:\Program Files\Amazon\AmazonCloudWatchAgent\'
        .\amazon-cloudwatch-agent-ctl.ps1 -m ec2 -a status
    
    # Linux
        sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -m ec2 -a status

# If not installed, install CloudWatch agent
https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/install-CloudWatch-Agent-on-EC2-Instance.html
    # Linux	
        sudo yum install amazon-cloudwatch-agent

        sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -m ec2 -a status

    # Windows	
        Invoke-WebRequest -Uri "https://amazoncloudwatch-agent.s3.amazonaws.com/windows/amd64/latest/amazon-cloudwatch-agent.msi" -UseBasicParsing -OutFile "c:\temp\amazon-cloudwatch-agent.msi"

        msiexec /i "c:\temp\amazon-cloudwatch-agent.msi"

        cd 'C:\Program Files\Amazon\AmazonCloudWatchAgent\'
        .\amazon-cloudwatch-agent-ctl.ps1 -m ec2 -a status

# Copy the config file to the relevant place
    # Linux
        cd /opt/aws/amazon-cloudwatch-agent/bin/
        vim /opt/aws/amazon-cloudwatch-agent/bin/config.json

    # Windows
        C:\Program Files\Amazon\AmazonCloudWatchAgent\config.json

# Restart CloudWatch agent
    # Linux
        sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -m ec2 -a fetch-config -c file:'/opt/aws/amazon-cloudwatch-agent/bin/config.json' -s

        sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -m ec2 -a status
    
    # Windows
		cd 'C:\Program Files\Amazon\AmazonCloudWatchAgent\'

        .\amazon-cloudwatch-agent-ctl.ps1 -m ec2 -a fetch-config -c file:'C:\Program Files\Amazon\AmazonCloudWatchAgent\config.json' -s

        .\amazon-cloudwatch-agent-ctl.ps1 -m ec2 -a status

# Check new metrics exist in CloudWatch

# If you have issues check the CloudWatch Agent logs
    # Windows
        C:\ProgramData\Amazon\AmazonCloudWatchAgent\Logs

    # Linux
        /opt/aws/amazon-cloudwatch-agent/logs/
```