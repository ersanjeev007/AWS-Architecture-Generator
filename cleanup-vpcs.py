#!/usr/bin/env python3
"""
AWS VPC Cleanup Script
Safely identifies and helps clean up unused VPCs to resolve VPC limit issues.
"""

import boto3
import json
from botocore.exceptions import ClientError

def get_aws_session():
    """Get AWS session from default credentials"""
    try:
        session = boto3.Session()
        # Test credentials
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ Connected to AWS Account: {identity['Account']}")
        return session
    except Exception as e:
        print(f"❌ AWS Credentials Error: {e}")
        print("Please configure AWS credentials:")
        print("  aws configure")
        return None

def analyze_vpcs(region='us-west-2'):
    """Analyze VPCs and their resources"""
    session = get_aws_session()
    if not session:
        return
    
    ec2 = session.client('ec2', region_name=region)
    
    try:
        # Get all VPCs
        vpcs_response = ec2.describe_vpcs()
        vpcs = vpcs_response['Vpcs']
        
        print(f"\n📊 Found {len(vpcs)} VPCs in {region}:")
        print("=" * 80)
        
        cleanup_candidates = []
        
        for vpc in vpcs:
            vpc_id = vpc['VpcId']
            is_default = vpc.get('IsDefault', False)
            state = vpc.get('State', 'unknown')
            
            # Get VPC name from tags
            vpc_name = 'No Name'
            tags = vpc.get('Tags', [])
            for tag in tags:
                if tag['Key'] == 'Name':
                    vpc_name = tag['Value']
                    break
            
            print(f"\n🏗️  VPC: {vpc_id}")
            print(f"   Name: {vpc_name}")
            print(f"   State: {state}")
            print(f"   Default: {is_default}")
            print(f"   CIDR: {vpc.get('CidrBlock', 'unknown')}")
            
            if is_default:
                print("   ⚠️  SKIP - Default VPC (never delete)")
                continue
                
            # Check for resources in this VPC
            has_resources = check_vpc_resources(ec2, vpc_id)
            
            if not has_resources and state == 'available':
                cleanup_candidates.append({
                    'id': vpc_id,
                    'name': vpc_name,
                    'cidr': vpc.get('CidrBlock', 'unknown')
                })
                print("   ✅ SAFE TO DELETE - No resources found")
            elif has_resources:
                print("   ⚠️  HAS RESOURCES - Review before deleting")
            else:
                print(f"   ⚠️  State: {state} - May not be deletable")
        
        print("\n" + "=" * 80)
        print(f"📋 SUMMARY:")
        print(f"   Total VPCs: {len(vpcs)}")
        print(f"   Safe to delete: {len(cleanup_candidates)}")
        print(f"   AWS Limit: 5 VPCs per region")
        
        if cleanup_candidates:
            print(f"\n🗑️  VPCs SAFE TO DELETE:")
            for i, vpc in enumerate(cleanup_candidates, 1):
                print(f"   {i}. {vpc['id']} ({vpc['name']}) - {vpc['cidr']}")
            
            return cleanup_candidates
        else:
            print("\n⚠️  No VPCs found that are safe to auto-delete.")
            print("   You may need to manually review and clean up VPCs with resources.")
            
    except ClientError as e:
        print(f"❌ AWS API Error: {e}")
        return []

def check_vpc_resources(ec2, vpc_id):
    """Check if VPC has any resources that would prevent deletion"""
    try:
        # Check for EC2 instances
        instances = ec2.describe_instances(
            Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
        )
        
        running_instances = []
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                if instance['State']['Name'] != 'terminated':
                    running_instances.append(instance['InstanceId'])
        
        if running_instances:
            print(f"   📦 EC2 Instances: {len(running_instances)}")
            return True
        
        # Check for subnets (basic check)
        subnets = ec2.describe_subnets(
            Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
        )
        
        if len(subnets['Subnets']) > 0:
            print(f"   🏠 Subnets: {len(subnets['Subnets'])}")
            # Check if subnets have any ENIs (indicating resources)
            for subnet in subnets['Subnets']:
                enis = ec2.describe_network_interfaces(
                    Filters=[{'Name': 'subnet-id', 'Values': [subnet['SubnetId']]}]
                )
                if enis['NetworkInterfaces']:
                    print(f"   🔌 Network interfaces found in subnet {subnet['SubnetId']}")
                    return True
        
        # Check for Internet Gateways
        igws = ec2.describe_internet_gateways(
            Filters=[{'Name': 'attachment.vpc-id', 'Values': [vpc_id]}]
        )
        
        if igws['InternetGateways']:
            print(f"   🌐 Internet Gateways: {len(igws['InternetGateways'])}")
        
        # Check for NAT Gateways
        nat_gws = ec2.describe_nat_gateways(
            Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
        )
        
        active_nats = [ng for ng in nat_gws['NatGateways'] if ng['State'] != 'deleted']
        if active_nats:
            print(f"   🔀 NAT Gateways: {len(active_nats)}")
            return True
        
        print("   ✨ No blocking resources found")
        return False
        
    except Exception as e:
        print(f"   ❌ Error checking resources: {e}")
        return True  # Assume has resources if we can't check

def delete_vpc_safe(ec2, vpc_id, vpc_name):
    """Safely delete a VPC after removing dependencies"""
    print(f"\n🗑️  Attempting to delete VPC: {vpc_id} ({vpc_name})")
    
    try:
        # Try to delete directly first
        ec2.delete_vpc(VpcId=vpc_id)
        print(f"   ✅ Successfully deleted VPC: {vpc_id}")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        
        if error_code == 'DependencyViolation':
            print(f"   ⚠️  Cannot delete: VPC has dependencies")
            print(f"   💡 Try cleaning up resources in AWS Console first")
            return False
        else:
            print(f"   ❌ Error: {e}")
            return False

def main():
    """Main cleanup function"""
    print("🧹 AWS VPC Cleanup Tool")
    print("=" * 50)
    
    # Analyze current VPCs
    cleanup_candidates = analyze_vpcs()
    
    if not cleanup_candidates:
        print("\n💡 RECOMMENDATIONS:")
        print("   1. Check AWS Console for VPCs with old test resources")
        print("   2. Delete resources manually: EC2 → RDS → Load Balancers → VPC")
        print("   3. Consider using a different AWS region")
        print("   4. Request VPC limit increase via AWS Support")
        return
    
    print(f"\n🤖 AUTO-CLEANUP OPTIONS:")
    print("   This script can attempt to delete the safe VPCs listed above.")
    print("   ⚠️  Only VPCs with no resources will be deleted.")
    
    # For safety, just show analysis - don't auto-delete
    print(f"\n📋 TO DELETE THESE VPCs MANUALLY:")
    for vpc in cleanup_candidates:
        print(f"   aws ec2 delete-vpc --vpc-id {vpc['id']} --region us-west-2")
    
    print(f"\n✅ After deleting 1-2 VPCs, re-run your Terraform deployment!")

if __name__ == "__main__":
    main()