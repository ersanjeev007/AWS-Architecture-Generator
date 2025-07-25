import uuid
import boto3
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from botocore.exceptions import ClientError, NoCredentialsError

from app.database import AWSAccountDB
from app.models.aws_account import (
    AWSAccountCreate, 
    AWSAccountUpdate, 
    AWSAccountResponse, 
    AWSAccountListItem
)
from app.utils.encryption import credential_encryption

class AWSAccountService:
    """Service for managing AWS accounts and credentials"""
    
    def create_account(self, db: Session, account_data: AWSAccountCreate) -> AWSAccountResponse:
        """Create new AWS account with encrypted credentials"""
        
        # Validate AWS credentials first
        is_valid = self._validate_credentials(
            account_data.aws_access_key_id,
            account_data.aws_secret_access_key,
            account_data.aws_session_token,
            account_data.aws_region
        )
        
        if not is_valid:
            raise ValueError("Invalid AWS credentials provided")
        
        # Encrypt credentials
        encrypted_access_key = credential_encryption.encrypt(account_data.aws_access_key_id)
        encrypted_secret_key = credential_encryption.encrypt(account_data.aws_secret_access_key)
        encrypted_session_token = credential_encryption.encrypt(account_data.aws_session_token) if account_data.aws_session_token else None
        
        # Create database record
        db_account = AWSAccountDB(
            id=str(uuid.uuid4()),
            account_name=account_data.account_name,
            aws_region=account_data.aws_region,
            description=account_data.description,
            encrypted_access_key=encrypted_access_key,
            encrypted_secret_key=encrypted_secret_key,
            encrypted_session_token=encrypted_session_token,
            is_active=True,
            last_validated=datetime.utcnow()
        )
        
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        
        return self._db_to_response(db_account)
    
    def list_accounts(self, db: Session, skip: int = 0, limit: int = 100) -> List[AWSAccountListItem]:
        """List all AWS accounts (without credentials)"""
        accounts = db.query(AWSAccountDB).offset(skip).limit(limit).all()
        return [self._db_to_list_item(account) for account in accounts]
    
    def get_account(self, db: Session, account_id: str) -> Optional[AWSAccountResponse]:
        """Get AWS account by ID (without credentials)"""
        account = db.query(AWSAccountDB).filter(AWSAccountDB.id == account_id).first()
        if not account:
            return None
        return self._db_to_response(account)
    
    def update_account(self, db: Session, account_id: str, account_update: AWSAccountUpdate) -> Optional[AWSAccountResponse]:
        """Update AWS account information (not credentials)"""
        account = db.query(AWSAccountDB).filter(AWSAccountDB.id == account_id).first()
        if not account:
            return None
        
        if account_update.account_name:
            account.account_name = account_update.account_name
        if account_update.aws_region:
            account.aws_region = account_update.aws_region
        if account_update.description is not None:
            account.description = account_update.description
        
        account.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(account)
        
        return self._db_to_response(account)
    
    def delete_account(self, db: Session, account_id: str) -> bool:
        """Delete AWS account"""
        account = db.query(AWSAccountDB).filter(AWSAccountDB.id == account_id).first()
        if not account:
            return False
        
        db.delete(account)
        db.commit()
        return True
    
    def validate_account(self, db: Session, account_id: str) -> bool:
        """Validate AWS account credentials"""
        account = db.query(AWSAccountDB).filter(AWSAccountDB.id == account_id).first()
        if not account:
            return False
        
        # Decrypt credentials
        access_key = credential_encryption.decrypt(account.encrypted_access_key)
        secret_key = credential_encryption.decrypt(account.encrypted_secret_key)
        session_token = credential_encryption.decrypt(account.encrypted_session_token) if account.encrypted_session_token else None
        
        # Validate credentials
        is_valid = self._validate_credentials(access_key, secret_key, session_token, account.aws_region)
        
        # Update validation status
        account.last_validated = datetime.utcnow()
        account.is_active = is_valid
        db.commit()
        
        return is_valid
    
    def get_credentials(self, db: Session, account_id: str) -> Optional[dict]:
        """Get decrypted credentials for deployment (internal use only)"""
        account = db.query(AWSAccountDB).filter(AWSAccountDB.id == account_id).first()
        if not account or not account.is_active:
            return None
        
        try:
            credentials = {
                'aws_access_key_id': credential_encryption.decrypt(account.encrypted_access_key),
                'aws_secret_access_key': credential_encryption.decrypt(account.encrypted_secret_key),
                'region_name': account.aws_region
            }
            
            if account.encrypted_session_token:
                credentials['aws_session_token'] = credential_encryption.decrypt(account.encrypted_session_token)
            
            return credentials
        except Exception:
            return None
    
    def _validate_credentials(self, access_key: str, secret_key: str, session_token: Optional[str], region: str) -> bool:
        """Validate AWS credentials by making a test API call"""
        try:
            # Create boto3 session with provided credentials
            session = boto3.Session(
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                aws_session_token=session_token,
                region_name=region
            )
            
            # Test credentials with a simple STS call
            sts = session.client('sts')
            sts.get_caller_identity()
            
            return True
            
        except (ClientError, NoCredentialsError):
            return False
        except Exception:
            return False
    
    def _db_to_response(self, db_account: AWSAccountDB) -> AWSAccountResponse:
        """Convert database model to response model"""
        return AWSAccountResponse(
            id=db_account.id,
            account_name=db_account.account_name,
            aws_region=db_account.aws_region,
            description=db_account.description,
            is_active=db_account.is_active,
            last_validated=db_account.last_validated,
            created_at=db_account.created_at,
            updated_at=db_account.updated_at
        )
    
    def _db_to_list_item(self, db_account: AWSAccountDB) -> AWSAccountListItem:
        """Convert database model to list item model"""
        return AWSAccountListItem(
            id=db_account.id,
            account_name=db_account.account_name,
            aws_region=db_account.aws_region,
            is_active=db_account.is_active,
            last_validated=db_account.last_validated
        )