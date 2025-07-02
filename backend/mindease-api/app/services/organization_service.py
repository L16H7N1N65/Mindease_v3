'''
Organization service for managing organizations and API keys.
'''
import logging
import secrets
import string
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.db.models.organization import ApiKey, OrganizationMember, Organization

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrganizationService:
    """Service for organization and API key management."""
    
    def __init__(self, db: Session):
        """
        Initialize the organization service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def get_user_organizations(self, user_id: int) -> List[Organization]:
        """
        Get organizations for a user.
        """
        try:
            # (old) memberships = self.db.query(Member).filter(Member.user_id == user_id).all()
            memberships = self.db.query(OrganizationMember).filter(
                OrganizationMember.user_id == user_id
            ).all()
            org_ids = [m.organization_id for m in memberships]
            if not org_ids:
                return []
            return self.db.query(Organization).filter(
                Organization.id.in_(org_ids)
            ).all()
        except Exception as e:
            logger.error(f"Error getting user organizations: {str(e)}")
            return []
    
    def create_organization(
        self,
        name: str,
        description: Optional[str] = None,
        logo_url: Optional[str] = None,
        is_active: bool = True,
        owner_id: Optional[int] = None
    ) -> Optional[Organization]:
        """
        Create a new organization and optionally add an owner member.
        """
        try:
            # Old implementation commented out
            # org = Organization(name=name, description=description)
            # self.db.add(org)
            # self.db.flush()
            # if owner_id:
            #     member = OrganizationMember(
            #         organization_id=org.id,
            #         user_id=owner_id,
            #         role="owner",
            #         is_active=True
            #     )
            #     self.db.add(OrganizationMember)
            # self.db.commit()
            # return org
            
            # New, corrected implementation:
            org = Organization(
                name=name,
                description=description,
                logo_url=logo_url,
                is_active=is_active
            )
            self.db.add(org)
            self.db.flush()  # populate org.id
            if owner_id:
                owner_membership = OrganizationMember(
                    organization_id=org.id,
                    user_id=owner_id,
                    role="owner",
                    is_active=True
                )
                self.db.add(owner_membership)
            self.db.commit()
            return org
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating organization: {str(e)}")
            return None
    
    def add_member(
        self,
        organization_id: int,
        user_id: int,
        role: str = "member",
        is_active: bool = True
    ) -> Optional[OrganizationMember]:
        """
        Add a member to an organization.
        """
        try:
            # Old implementation commented out
            # org = self.db.query(Organization).get(organization_id)
            # existing = self.db.query(Member)...
            # membership = Member(...)
            # self.db.add(membership)
            # self.db.commit()
            # return membership
            
            # New, corrected implementation:
            org = self.db.query(Organization).get(organization_id)
            if not org:
                logger.error(f"Organization {organization_id} not found")
                return None
            existing = (
                self.db.query(OrganizationMember)
                .filter(
                    OrganizationMember.organization_id == organization_id,
                    OrganizationMember.user_id == user_id
                )
                .first()
            )
            if existing:
                return existing
            membership = OrganizationMember(
                organization_id=organization_id,
                user_id=user_id,
                role=role,
                is_active=is_active
            )
            self.db.add(membership)
            self.db.commit()
            return membership
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding member: {e}")
            return None
    
    def create_api_key(
        self,
        organization_id: int,
        key_name: str,
        expires_at: Optional[datetime] = None
    ) -> Optional[Tuple[ApiKey, str]]:
        """
        Create a new API key for an organization.
        """
        try:
            org = self.db.query(Organization).filter(
                Organization.id == organization_id
            ).first()
            if not org:
                logger.error(f"Organization {organization_id} not found")
                return None
            key_value = self._generate_api_key()
            api_key = ApiKey(
                organization_id=organization_id,
                key_name=key_name,
                key_hash=self._hash_api_key(key_value),
                expires_at=expires_at
            )
            self.db.add(api_key)
            self.db.commit()
            return api_key, key_value
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating API key: {str(e)}")
            return None
    
    def validate_api_key(self, key_value: str) -> Optional[Organization]:
        """
        Validate an API key and return its organization.
        """
        try:
            key_hash = self._hash_api_key(key_value)
            api_key = self.db.query(ApiKey).filter(
                ApiKey.key_hash == key_hash,
                ApiKey.is_active == True
            ).first()
            if not api_key:
                return None
            if api_key.expires_at and api_key.expires_at < datetime.utcnow():
                return None
            return self.db.query(Organization).get(api_key.organization_id)
        except Exception as e:
            logger.error(f"Error validating API key: {str(e)}")
            return None
    
    def _generate_api_key(self) -> str:
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))

    def _hash_api_key(self, key_value: str) -> str:
        # In production use a secure hash (e.g. passlib)
        return key_value
