import uuid
import tempfile
import subprocess
import os
import threading
import asyncio
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.database import DeploymentDB
from app.models.aws_account import DeploymentRequest, DeploymentResponse, DestroyRequest
from app.services.aws_account_service import AWSAccountService
from app.services.project_service import ProjectService

class DeploymentService:
    """Service for deploying infrastructure using Terraform or CloudFormation"""
    
    def __init__(self):
        self.aws_account_service = AWSAccountService()
        self.project_service = ProjectService()
    
    def deploy_infrastructure(self, db: Session, deployment_request: DeploymentRequest) -> DeploymentResponse:
        """Deploy infrastructure to AWS (starts async deployment and returns immediately)"""
        
        # Create deployment record
        deployment_id = str(uuid.uuid4())
        deployment = DeploymentDB(
            id=deployment_id,
            project_id=deployment_request.project_id,
            aws_account_id=deployment_request.aws_account_id,
            template_type=deployment_request.template_type,
            status="running",
            dry_run=deployment_request.dry_run
        )
        
        db.add(deployment)
        db.commit()
        
        # Start async deployment in background thread
        thread = threading.Thread(
            target=self._run_deployment_async,
            args=(deployment_id, deployment_request),
            daemon=True
        )
        thread.start()
        
        # Return immediately with running status
        return DeploymentResponse(
            deployment_id=deployment_id,
            status="running",
            message="Deployment started. Check status using deployment_id.",
            output=""
        )
    
    def _run_deployment_async(self, deployment_id: str, deployment_request: DeploymentRequest):
        """Run the actual deployment in background thread"""
        from app.database import SessionLocal
        
        # Create new DB session for this thread
        db = SessionLocal()
        
        try:
            # Get the deployment record
            deployment = db.query(DeploymentDB).filter(DeploymentDB.id == deployment_id).first()
            if not deployment:
                return
            
            # Get AWS credentials
            credentials = self.aws_account_service.get_credentials(db, deployment_request.aws_account_id)
            if not credentials:
                raise ValueError("Invalid or inactive AWS account")
            
            # Get project and template
            project = self.project_service.get_project(db, deployment_request.project_id)
            if not project:
                raise ValueError("Project not found")
            
            if deployment_request.template_type == "terraform":
                result = self._deploy_terraform(
                    project.architecture_data.get("terraform_template", ""),
                    credentials,
                    deployment_request.dry_run,
                    project
                )
            elif deployment_request.template_type == "cloudformation":
                result = self._deploy_cloudformation(
                    project.architecture_data.get("cloudformation_template", ""),
                    credentials,
                    deployment_request.dry_run
                )
            else:
                raise ValueError("Invalid template type")
            
            # Update deployment record with success
            deployment.status = "success"
            deployment.output = result.get("output", "")
            deployment.stack_name = result.get("stack_name", "")
            deployment.terraform_state_path = result.get("terraform_state_path", "")
            deployment.updated_at = datetime.utcnow()
            
            db.commit()
            
        except Exception as e:
            # Update deployment record with failure
            deployment.status = "failed"
            deployment.error = str(e)
            deployment.updated_at = datetime.utcnow()
            
            db.commit()
            
        finally:
            db.close()
    
    def get_deployment_status(self, db: Session, deployment_id: str) -> Optional[DeploymentResponse]:
        """Get deployment status"""
        deployment = db.query(DeploymentDB).filter(DeploymentDB.id == deployment_id).first()
        if not deployment:
            return None
        
        return DeploymentResponse(
            deployment_id=deployment.id,
            status=deployment.status,
            message=f"Deployment {deployment.status}",
            output=deployment.output,
            error=deployment.error
        )
    
    def destroy_infrastructure(self, db: Session, destroy_request: DestroyRequest) -> DeploymentResponse:
        """Destroy deployed infrastructure (starts async destroy and returns immediately)"""
        
        # Get original deployment record
        original_deployment = db.query(DeploymentDB).filter(
            DeploymentDB.id == destroy_request.deployment_id
        ).first()
        
        if not original_deployment:
            raise ValueError("Original deployment not found")
        
        if original_deployment.status != "success":
            raise ValueError("Can only destroy successfully deployed infrastructure")
        
        if original_deployment.dry_run:
            raise ValueError("Cannot destroy a dry run deployment")
        
        # Create new deployment record for destroy operation
        destroy_deployment_id = str(uuid.uuid4())
        destroy_deployment = DeploymentDB(
            id=destroy_deployment_id,
            project_id=original_deployment.project_id,
            aws_account_id=destroy_request.aws_account_id,
            template_type=destroy_request.template_type,
            status="running",
            dry_run=destroy_request.dry_run
        )
        
        db.add(destroy_deployment)
        db.commit()
        
        # Start async destroy in background thread
        thread = threading.Thread(
            target=self._run_destroy_async,
            args=(destroy_deployment_id, destroy_request, original_deployment.id),
            daemon=True
        )
        thread.start()
        
        # Return immediately with running status
        return DeploymentResponse(
            deployment_id=destroy_deployment_id,
            status="running",
            message="Destroy operation started. Check status using deployment_id.",
            output=""
        )
    
    def _run_destroy_async(self, destroy_deployment_id: str, destroy_request: DestroyRequest, original_deployment_id: str):
        """Run the actual destroy operation in background thread"""
        from app.database import SessionLocal
        
        # Create new DB session for this thread
        db = SessionLocal()
        
        try:
            # Get the destroy deployment record
            destroy_deployment = db.query(DeploymentDB).filter(DeploymentDB.id == destroy_deployment_id).first()
            original_deployment = db.query(DeploymentDB).filter(DeploymentDB.id == original_deployment_id).first()
            
            if not destroy_deployment or not original_deployment:
                return
            
            # Get AWS credentials
            credentials = self.aws_account_service.get_credentials(db, destroy_request.aws_account_id)
            if not credentials:
                raise ValueError("Invalid or inactive AWS account")
            
            # Get project and template
            project = self.project_service.get_project(db, original_deployment.project_id)
            if not project:
                raise ValueError("Project not found")
            
            if destroy_request.template_type == "terraform":
                result = self._destroy_terraform(
                    project.architecture_data.get("terraform_template", ""),
                    credentials,
                    original_deployment.terraform_state_path,
                    destroy_request.dry_run,
                    destroy_request.force_destroy,
                    project
                )
            elif destroy_request.template_type == "cloudformation":
                result = self._destroy_cloudformation(
                    credentials,
                    original_deployment.stack_name,
                    destroy_request.dry_run,
                    destroy_request.force_destroy
                )
            else:
                raise ValueError("Invalid template type")
            
            # Update destroy deployment record with success
            destroy_deployment.status = "success"
            destroy_deployment.output = result.get("output", "")
            destroy_deployment.updated_at = datetime.utcnow()
            
            # Update original deployment status if actually destroyed
            if not destroy_request.dry_run:
                original_deployment.status = "destroyed"
                original_deployment.updated_at = datetime.utcnow()
            
            db.commit()
            
        except Exception as e:
            # Update destroy deployment record with failure
            destroy_deployment.status = "failed"
            destroy_deployment.error = str(e)
            destroy_deployment.updated_at = datetime.utcnow()
            
            db.commit()
            
        finally:
            db.close()
    
    def list_deployments(self, db: Session, project_id: str) -> list:
        """List all deployments for a project"""
        deployments = db.query(DeploymentDB).filter(
            DeploymentDB.project_id == project_id
        ).order_by(DeploymentDB.created_at.desc()).all()
        
        return [
            {
                "id": d.id,
                "project_id": d.project_id,
                "aws_account_id": d.aws_account_id,
                "template_type": d.template_type,
                "status": d.status,
                "dry_run": d.dry_run,
                "stack_name": d.stack_name,
                "terraform_state_path": d.terraform_state_path,
                "output": d.output,
                "error": d.error,
                "created_at": d.created_at,
                "updated_at": d.updated_at
            }
            for d in deployments
        ]
    
    def get_project_deployment_status(self, db: Session, project_id: str) -> dict:
        """Get current deployment status summary for a project"""
        deployments = db.query(DeploymentDB).filter(
            DeploymentDB.project_id == project_id
        ).order_by(DeploymentDB.created_at.desc()).all()
        
        # Find active deployments (successful, non-dry-run, not destroyed)
        active_deployments = [
            d for d in deployments 
            if d.status == "success" and not d.dry_run
        ]
        
        # Check if any have been destroyed
        destroyed_deployments = [
            d for d in deployments 
            if d.status == "destroyed"
        ]
        
        # Find most recent successful deployment
        current_deployment = None
        if active_deployments:
            # Filter out deployments that have been destroyed
            destroyed_ids = {d.id for d in destroyed_deployments}
            live_deployments = [
                d for d in active_deployments 
                if d.id not in destroyed_ids
            ]
            
            if live_deployments:
                current_deployment = live_deployments[0]
        
        # Count deployments by type and status
        terraform_deployments = len([d for d in deployments if d.template_type == "terraform" and d.status == "success" and not d.dry_run])
        cloudformation_deployments = len([d for d in deployments if d.template_type == "cloudformation" and d.status == "success" and not d.dry_run])
        
        return {
            "project_id": project_id,
            "is_deployed": current_deployment is not None,
            "current_deployment": {
                "id": current_deployment.id,
                "template_type": current_deployment.template_type,
                "stack_name": current_deployment.stack_name,
                "aws_account_id": current_deployment.aws_account_id,
                "deployed_at": current_deployment.created_at,
                "last_updated": current_deployment.updated_at
            } if current_deployment else None,
            "deployment_history": {
                "total_deployments": len([d for d in deployments if d.status == "success" and not d.dry_run]),
                "terraform_deployments": terraform_deployments,
                "cloudformation_deployments": cloudformation_deployments,
                "destroyed_deployments": len(destroyed_deployments),
                "failed_deployments": len([d for d in deployments if d.status == "failed"]),
                "last_activity": deployments[0].updated_at if deployments else None
            }
        }
    
    def _deploy_terraform(self, terraform_template: str, credentials: dict, dry_run: bool, project=None) -> dict:
        """Deploy using Terraform"""
        if not terraform_template:
            raise ValueError("No Terraform template found")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write Terraform template to file
            tf_file = os.path.join(temp_dir, "main.tf")
            with open(tf_file, 'w') as f:
                f.write(terraform_template)
            
            # Create terraform.tfvars file with project variables
            if project:
                tfvars_content = self._create_terraform_vars(project, credentials)
                tfvars_file = os.path.join(temp_dir, "terraform.tfvars")
                with open(tfvars_file, 'w') as f:
                    f.write(tfvars_content)
            
            # Set environment variables for AWS credentials
            env = os.environ.copy()
            env.update({
                'AWS_ACCESS_KEY_ID': credentials['aws_access_key_id'],
                'AWS_SECRET_ACCESS_KEY': credentials['aws_secret_access_key'],
                'AWS_DEFAULT_REGION': credentials['region_name']
            })
            
            if 'aws_session_token' in credentials:
                env['AWS_SESSION_TOKEN'] = credentials['aws_session_token']
            
            try:
                # Initialize Terraform
                init_result = subprocess.run(
                    ['terraform', 'init'],
                    cwd=temp_dir,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if init_result.returncode != 0:
                    raise Exception(f"Terraform init failed: {init_result.stderr}")
                
                # Plan or Apply
                if dry_run:
                    plan_result = subprocess.run(
                        ['terraform', 'plan'],
                        cwd=temp_dir,
                        env=env,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    if plan_result.returncode != 0:
                        raise Exception(f"Terraform plan failed: {plan_result.stderr}")
                    
                    return {"output": plan_result.stdout}
                else:
                    apply_result = subprocess.run(
                        ['terraform', 'apply', '-auto-approve'],
                        cwd=temp_dir,
                        env=env,
                        capture_output=True,
                        text=True,
                        timeout=1800  # 30 minutes timeout
                    )
                    
                    if apply_result.returncode != 0:
                        raise Exception(f"Terraform apply failed: {apply_result.stderr}")
                    
                    return {
                        "output": apply_result.stdout,
                        "terraform_state_path": os.path.join(temp_dir, "terraform.tfstate")
                    }
                    
            except subprocess.TimeoutExpired:
                raise Exception("Terraform command timed out")
            except FileNotFoundError:
                raise Exception("Terraform not found. Please install Terraform on the server.")
    
    def _deploy_cloudformation(self, cf_template: str, credentials: dict, dry_run: bool) -> dict:
        """Deploy using CloudFormation"""
        if not cf_template:
            raise ValueError("No CloudFormation template found")
        
        import boto3
        
        # Create CloudFormation client
        session = boto3.Session(
            aws_access_key_id=credentials['aws_access_key_id'],
            aws_secret_access_key=credentials['aws_secret_access_key'],
            aws_session_token=credentials.get('aws_session_token'),
            region_name=credentials['region_name']
        )
        
        cf_client = session.client('cloudformation')
        
        try:
            stack_name = f"aws-arch-gen-{uuid.uuid4().hex[:8]}"
            
            if dry_run:
                # Validate template
                response = cf_client.validate_template(TemplateBody=cf_template)
                return {"output": f"CloudFormation template validation successful. Parameters: {response.get('Parameters', [])}, Capabilities: {response.get('Capabilities', [])}"}
            else:
                # Create stack
                response = cf_client.create_stack(
                    StackName=stack_name,
                    TemplateBody=cf_template,
                    Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']
                )
                
                stack_id = response['StackId']
                
                # Wait for stack creation (with timeout)
                waiter = cf_client.get_waiter('stack_create_complete')
                waiter.wait(
                    StackName=stack_id,
                    WaiterConfig={'Delay': 30, 'MaxAttempts': 60}  # 30 minutes max
                )
                
                # Get stack outputs
                stack_info = cf_client.describe_stacks(StackName=stack_id)
                outputs = stack_info['Stacks'][0].get('Outputs', [])
                
                output_text = f"Stack created successfully: {stack_id}\n"
                if outputs:
                    output_text += "\nOutputs:\n"
                    for output in outputs:
                        output_text += f"- {output['OutputKey']}: {output['OutputValue']}\n"
                
                return {
                    "output": output_text,
                    "stack_name": stack_name
                }
                
        except Exception as e:
            raise Exception(f"CloudFormation deployment failed: {str(e)}")
    
    def _destroy_terraform(self, terraform_template: str, credentials: dict, state_path: str, dry_run: bool, force_destroy: bool, project=None) -> dict:
        """Destroy using Terraform"""
        if not terraform_template:
            raise ValueError("No Terraform template found")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write Terraform template to file
            tf_file = os.path.join(temp_dir, "main.tf")
            with open(tf_file, 'w') as f:
                f.write(terraform_template)
            
            # Create terraform.tfvars file with project variables
            if project:
                tfvars_content = self._create_terraform_vars(project, credentials)
                tfvars_file = os.path.join(temp_dir, "terraform.tfvars")
                with open(tfvars_file, 'w') as f:
                    f.write(tfvars_content)
            
            # If we have a state file, restore it
            if state_path and os.path.exists(state_path):
                import shutil
                shutil.copy(state_path, os.path.join(temp_dir, "terraform.tfstate"))
            
            # Set environment variables for AWS credentials
            env = os.environ.copy()
            env.update({
                'AWS_ACCESS_KEY_ID': credentials['aws_access_key_id'],
                'AWS_SECRET_ACCESS_KEY': credentials['aws_secret_access_key'],
                'AWS_DEFAULT_REGION': credentials['region_name']
            })
            
            if 'aws_session_token' in credentials:
                env['AWS_SESSION_TOKEN'] = credentials['aws_session_token']
            
            try:
                # Initialize Terraform
                init_result = subprocess.run(
                    ['terraform', 'init'],
                    cwd=temp_dir,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if init_result.returncode != 0:
                    raise Exception(f"Terraform init failed: {init_result.stderr}")
                
                # Plan or Destroy
                if dry_run:
                    plan_result = subprocess.run(
                        ['terraform', 'plan', '-destroy'],
                        cwd=temp_dir,
                        env=env,
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    if plan_result.returncode != 0:
                        raise Exception(f"Terraform destroy plan failed: {plan_result.stderr}")
                    
                    return {"output": plan_result.stdout}
                else:
                    destroy_args = ['terraform', 'destroy', '-auto-approve']
                    if force_destroy:
                        destroy_args.append('-refresh=false')
                    
                    destroy_result = subprocess.run(
                        destroy_args,
                        cwd=temp_dir,
                        env=env,
                        capture_output=True,
                        text=True,
                        timeout=1800  # 30 minutes timeout
                    )
                    
                    if destroy_result.returncode != 0:
                        raise Exception(f"Terraform destroy failed: {destroy_result.stderr}")
                    
                    return {"output": destroy_result.stdout}
                    
            except subprocess.TimeoutExpired:
                raise Exception("Terraform destroy command timed out")
            except FileNotFoundError:
                raise Exception("Terraform not found. Please install Terraform on the server.")
    
    def _destroy_cloudformation(self, credentials: dict, stack_name: str, dry_run: bool, force_destroy: bool) -> dict:
        """Destroy using CloudFormation"""
        if not stack_name:
            raise ValueError("No CloudFormation stack name found")
        
        import boto3
        
        # Create CloudFormation client
        session = boto3.Session(
            aws_access_key_id=credentials['aws_access_key_id'],
            aws_secret_access_key=credentials['aws_secret_access_key'],
            aws_session_token=credentials.get('aws_session_token'),
            region_name=credentials['region_name']
        )
        
        cf_client = session.client('cloudformation')
        
        try:
            if dry_run:
                # Get stack info to show what would be deleted
                try:
                    stack_info = cf_client.describe_stacks(StackName=stack_name)
                    stack = stack_info['Stacks'][0]
                    
                    output_text = f"CloudFormation destroy dry run for stack: {stack_name}\n"
                    output_text += f"Stack Status: {stack['StackStatus']}\n"
                    output_text += f"Created: {stack['CreationTime']}\n"
                    
                    # List stack resources
                    resources = cf_client.list_stack_resources(StackName=stack_name)
                    output_text += f"\nResources that would be deleted:\n"
                    for resource in resources['StackResourceSummaries']:
                        output_text += f"- {resource['ResourceType']}: {resource['LogicalResourceId']}\n"
                    
                    return {"output": output_text}
                    
                except cf_client.exceptions.ClientError as e:
                    if 'does not exist' in str(e):
                        return {"output": f"Stack {stack_name} does not exist or has already been deleted"}
                    raise
                    
            else:
                # Delete stack
                try:
                    cf_client.delete_stack(StackName=stack_name)
                    
                    # Wait for stack deletion (with timeout)
                    waiter = cf_client.get_waiter('stack_delete_complete')
                    waiter.wait(
                        StackName=stack_name,
                        WaiterConfig={'Delay': 30, 'MaxAttempts': 60}  # 30 minutes max
                    )
                    
                    return {"output": f"Stack {stack_name} deleted successfully"}
                    
                except cf_client.exceptions.ClientError as e:
                    if 'does not exist' in str(e):
                        return {"output": f"Stack {stack_name} does not exist or has already been deleted"}
                    elif force_destroy and 'DELETE_FAILED' in str(e):
                        # Try to force delete by retaining resources
                        cf_client.delete_stack(
                            StackName=stack_name,
                            RetainResources=True
                        )
                        return {"output": f"Stack {stack_name} force deleted (some resources may be retained)"}
                    else:
                        raise Exception(f"CloudFormation delete failed: {str(e)}")
                
        except Exception as e:
            raise Exception(f"CloudFormation destruction failed: {str(e)}")
    
    def _create_terraform_vars(self, project, credentials: dict) -> str:
        """Create terraform.tfvars content from project data"""
        import json
        
        # Clean project name for AWS resource naming
        project_name_clean = project.project_name.lower().replace(' ', '-').replace('_', '-')
        
        # Start with basic project variables
        tfvars = f'''# Terraform variables for project: {project.project_name}
project_name = "{project_name_clean}"
region = "{credentials['region_name']}"
'''
        
        # Add questionnaire data as variables if available
        if project.questionnaire_data:
            questionnaire = project.questionnaire_data
            
            # Extract common variables from questionnaire
            if 'environment' in questionnaire:
                tfvars += f'environment = "{questionnaire["environment"]}"\n'
            
            if 'company_name' in questionnaire:
                tfvars += f'company_name = "{questionnaire["company_name"]}"\n'
            
            if 'budget_range' in questionnaire:
                tfvars += f'budget_range = "{questionnaire["budget_range"]}"\n'
            
            if 'expected_users' in questionnaire:
                tfvars += f'expected_users = "{questionnaire["expected_users"]}"\n'
            
            if 'compliance_requirements' in questionnaire:
                compliance_list = questionnaire["compliance_requirements"]
                if isinstance(compliance_list, list):
                    compliance_str = '", "'.join(compliance_list)
                    tfvars += f'compliance_requirements = ["{compliance_str}"]\n'
                else:
                    tfvars += f'compliance_requirements = ["{compliance_list}"]\n'
            
            if 'backup_requirements' in questionnaire:
                tfvars += f'backup_requirements = "{questionnaire["backup_requirements"]}"\n'
            
            if 'monitoring_level' in questionnaire:
                tfvars += f'monitoring_level = "{questionnaire["monitoring_level"]}"\n'
            
            if 'high_availability' in questionnaire:
                tfvars += f'high_availability = {str(questionnaire["high_availability"]).lower()}\n'
            
            if 'multi_region' in questionnaire:
                tfvars += f'multi_region = {str(questionnaire["multi_region"]).lower()}\n'
            
            # Add application-specific variables
            if 'application_type' in questionnaire:
                tfvars += f'application_type = "{questionnaire["application_type"]}"\n'
            
            if 'database_type' in questionnaire:
                tfvars += f'database_type = "{questionnaire["database_type"]}"\n'
            
            if 'storage_requirements' in questionnaire:
                tfvars += f'storage_requirements = "{questionnaire["storage_requirements"]}"\n'
            
            # Add security-related variables
            if 'security_level' in questionnaire:
                tfvars += f'security_level = "{questionnaire["security_level"]}"\n'
            
            if 'data_sensitivity' in questionnaire:
                tfvars += f'data_sensitivity = "{questionnaire["data_sensitivity"]}"\n'
            
            if 'encryption_requirements' in questionnaire:
                tfvars += f'encryption_requirements = "{questionnaire["encryption_requirements"]}"\n'
        
        # Add project description if available
        if project.description:
            # Escape quotes in description
            escaped_description = project.description.replace('"', '\\"').replace('\n', '\\n')
            tfvars += f'project_description = "{escaped_description}"\n'
        
        # Add timestamp for unique resource naming
        from datetime import datetime
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        tfvars += f'deployment_timestamp = "{timestamp}"\n'
        
        # Add additional required variables with defaults
        tfvars += f'services = {{\n'
        if project.questionnaire_data:
            questionnaire = project.questionnaire_data
            if 'database' in questionnaire:
                tfvars += f'  database = "{questionnaire["database"]}"\n'
            if 'load_balancer' in questionnaire:
                tfvars += f'  load_balancer = "application"\n'
            if 'lambda' in questionnaire:
                tfvars += f'  lambda = "true"\n'
        tfvars += f'}}\n'
        
        # Security-related variables
        tfvars += f'enable_bastion = false\n'
        tfvars += f'allowed_ssh_cidrs = ["10.0.0.0/8"]\n'
        tfvars += f'enable_deletion_protection = false\n'
        tfvars += f'enable_scp = false\n'
        
        return tfvars