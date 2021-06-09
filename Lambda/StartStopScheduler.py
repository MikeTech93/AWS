import boto3
import time
region = 'eu-west-1'
ec2 = boto3.client('ec2', region_name=region)
rds = boto3.client('rds', region_name=region)
db_clusters = rds.describe_db_clusters()
db_instances = rds.describe_db_instances()

schedule_enabled_key = 'ScheduleEnabled'
schedule_enabled_value = '1'
current_hour = time.strftime('%H').lstrip('0')
start_enable_key = 'WakeAt'
stop_enable_key = 'SleepAt'

def get_tags_for_db(db_arn):
    instance_tags = rds.list_tags_for_resource(ResourceName=db_arn)
    return instance_tags['TagList']

def list_rds_instances_to_start_at_current_hour():
    hour_to_enable_key = start_enable_key

    print('Trying to find rds instances scheduled to startup at: ' + str(current_hour)+'h')
    
    instancelist = []
    for db in db_instances['DBInstances']:
        if db['DBInstanceStatus'] != 'stopped':
            continue

        db_tags = get_tags_for_db(db['DBInstanceArn'])
        is_scheduling_enabled = False
        is_time_to_start = False
        for tag in db_tags:
            if tag['Key'] == schedule_enabled_key and tag['Value'] == schedule_enabled_value:
                is_scheduling_enabled = True
            if tag['Key'] == hour_to_enable_key and tag['Value'].lstrip('0') == current_hour:
                is_time_to_start = True
        
        if is_scheduling_enabled and is_time_to_start:
            instancelist.append(db['DBInstanceIdentifier'])
    
    print('Found rds instances to start: ' + str(instancelist))
    return instancelist

def list_rds_instances_to_stop_at_current_hour():
    hour_to_enable_key = stop_enable_key
    
    print('Trying to find rds instances scheduled to stop at: ' + str(current_hour)+'h')
    
    instancelist = []
    for db in db_instances['DBInstances']:
        if db['DBInstanceStatus'] != 'available':
            continue

        db_tags = get_tags_for_db(db['DBInstanceArn'])
        is_scheduling_enabled = False
        is_time_to_stop = False
        for tag in db_tags:
            if tag['Key'] == schedule_enabled_key and tag['Value'] == schedule_enabled_value:
                is_scheduling_enabled = True
            if tag['Key'] == hour_to_enable_key and tag['Value'].lstrip('0') == current_hour:
                is_time_to_stop = True
        
        if is_scheduling_enabled and is_time_to_stop:
            instancelist.append(db['DBInstanceIdentifier'])
    
    print('Found rds instances to stop: ' + str(instancelist))
    return instancelist

def list_rds_clusters_to_start_at_current_hour():
    hour_to_enable_key = start_enable_key;
    
    print('Trying to find rds clusters scheduled to startup at: ' + str(current_hour)+'h')
    
    clusterlist = []
    for db in db_clusters['DBClusters']:
        if db['Status'] != 'stopped':
            continue

        db_tags = get_tags_for_db(db['DBClusterArn'])
        is_scheduling_enabled = False
        is_time_to_start = False
        for tag in db_tags:
            if tag['Key'] == schedule_enabled_key and tag['Value'] == schedule_enabled_value:
                is_scheduling_enabled = True
            if tag['Key'] == hour_to_enable_key and tag['Value'].lstrip('0') == current_hour:
                is_time_to_start = True
        
        if is_scheduling_enabled and is_time_to_start:
            clusterlist.append(db['DBClusterIdentifier'])
    
    print('Found rds clusters to start: ' + str(clusterlist))
    return clusterlist

def list_rds_clusters_to_stop_at_current_hour():
    hour_to_enable_key = stop_enable_key;
    
    print('Trying to find rds clusters scheduled to stop at: ' + str(current_hour)+'h')
    
    clusterlist = []
    for db in db_clusters['DBClusters']:
        if db['Status'] != 'available':
            continue

        db_tags = get_tags_for_db(db['DBClusterArn'])
        is_scheduling_enabled = False
        is_time_to_stop = False
        for tag in db_tags:
            if tag['Key'] == schedule_enabled_key and tag['Value'] == schedule_enabled_value:
                is_scheduling_enabled = True
            if tag['Key'] == hour_to_enable_key and tag['Value'].lstrip('0') == current_hour:
                is_time_to_stop = True
        
        if is_scheduling_enabled and is_time_to_stop:
            clusterlist.append(db['DBClusterIdentifier'])
    
    print('Found rds clusters to stop: ' + str(clusterlist))
    return clusterlist

def list_ec2_instances_to_start_at_current_hour():
    hour_to_enable_key = start_enable_key;
    
    print('Trying to find ec2 instances scheduled to startup at: ' + str(current_hour)+'h')

    response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:'+schedule_enabled_key,
                'Values': [schedule_enabled_value]
            },
            {
                'Name': 'tag:'+hour_to_enable_key,
                'Values': [current_hour, "0"+current_hour]
            },
            {
                'Name': 'instance-state-name',
                'Values': ['stopped']
            }
        ]
    )
    instancelist = []
    for reservation in (response["Reservations"]):
        for instance in reservation["Instances"]:
            instancelist.append(instance["InstanceId"])
    
    print('Found ec2 instances to start: ' + str(instancelist))
    return instancelist

def list_ec2_instances_to_stop_at_current_hour():
    hour_to_enable_key = stop_enable_key;
    
    print('Trying to find ec2 instances scheduled to shutdown at: ' + str(current_hour)+'h')

    response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:'+schedule_enabled_key,
                'Values': [schedule_enabled_value]
            },
            {
                'Name': 'tag:'+hour_to_enable_key,
                'Values': [current_hour, "0"+current_hour]
            },
            {
                'Name': 'instance-state-name',
                'Values': ['running']
            }
        ]
    )
    instancelist = []
    for reservation in (response["Reservations"]):
        for instance in reservation["Instances"]:
            instancelist.append(instance["InstanceId"])
    
    print('Found ec2 instances to stop: ' + str(instancelist))
    return instancelist

def lambda_handler(event, context):
    
    #EC2
    instances = list_ec2_instances_to_stop_at_current_hour()
    if instances:
        ec2.stop_instances(InstanceIds=instances)
        print('Stopped ec2 instances: ' + str(instances))
    else:
        print('No ec2 instances found to stop')
    
    instances = list_ec2_instances_to_start_at_current_hour()
    if instances:
        ec2.start_instances(InstanceIds=instances)
        print('Started ec2 instances: ' + str(instances))
    else:
        print('No ec2 instances found to start')
    
    # RDS Clusters
    clusters = list_rds_clusters_to_stop_at_current_hour()
    if clusters:
        for cluster in clusters:
            rds.stop_db_cluster(DBClusterIdentifier=cluster)
        print('Stopped rds clusters: ' + str(clusters))
    else:
        print('No rds clusters found to stop')
    
    clusters = list_rds_clusters_to_start_at_current_hour()
    if clusters:
        for cluster in clusters:
            rds.start_db_cluster(DBClusterIdentifier=cluster)
        print('Started rds clusters: ' + str(clusters))
    else:
        print('No rds clusters found to start')
    
    # RDS Instances
    rds_instances = list_rds_instances_to_stop_at_current_hour()
    if rds_instances:
        for rds_instance in rds_instances:
            rds.stop_db_instance(DBInstanceIdentifier=rds_instance)
        print('Stopped rds instances: ' + str(rds_instances))
    else:
        print('No rds instances found to stop')
    
    rds_instances = list_rds_instances_to_start_at_current_hour()
    if rds_instances:
        for rds_instance in rds_instances:
            rds.start_db_instance(DBInstanceIdentifier=rds_instance)
        print('Started rds instances: ' + str(rds_instances))
    else:
        print('No rds instances found to start')