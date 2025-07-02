"""
Organization management router for multi-tenant functionality
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.db.models import User, Organization, OrganizationMember, ApiKey
from app.schemas.organization import (
    OrganizationCreate, OrganizationResponse, OrganizationUpdate,
    OrganizationMemberResponse, OrganizationMemberUpdate,
    ApiKeyCreate, ApiKeyResponse
)
from app.core.security import get_current_active_user, check_user_role

# router = APIRouter(
#     prefix="/organizations",
#     tags=["organizations"]
# )
router = APIRouter(tags=["organizations"])
# Organization Management Endpoints

@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    organization: OrganizationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new organization.
    
    - Only admin users can create organizations
    - Creates organization with the current user as owner
    """
    # Check if user has admin role
    if not check_user_role(current_user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create organizations"
        )
    
    # Check if organization name already exists
    existing_org = db.query(Organization).filter(
        Organization.name == organization.name
    ).first()
    
    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization name already exists"
        )
    
    db_organization = Organization(
        name=organization.name,
        description=organization.description,
        organization_type=organization.organization_type,
        contact_email=organization.contact_email,
        contact_phone=organization.contact_phone,
        address=organization.address,
        website=organization.website,
        is_active=True
    )
    
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)
    
    # Add current user as organization owner
    owner_membership = OrganizationMember(
        organization_id=db_organization.id,
        user_id=current_user.id,
        role="owner",
        is_active=True
    )
    
    db.add(owner_membership)
    db.commit()
    
    return db_organization

@router.get("", response_model=List[OrganizationResponse])
async def get_organizations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    organization_type: Optional[str] = Query(None, description="Filter by organization type"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get organizations.
    
    - Admin users see all organizations
    - Regular users see only organizations they belong to
    """
    if check_user_role(current_user, "admin"):
        # Admin can see all organizations
        query = db.query(Organization).filter(Organization.is_active == True)
    else:
        # Regular users see only their organizations
        query = db.query(Organization).join(OrganizationMember).filter(
            and_(
                Organization.is_active == True,
                OrganizationMember.user_id == current_user.id,
                OrganizationMember.is_active == True
            )
        )
    
    if organization_type:
        query = query.filter(Organization.organization_type == organization_type)
    
    organizations = query.order_by(Organization.name).offset(skip).limit(limit).all()
    
    return organizations

@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific organization by ID."""
    # Check if user has access to this organization
    if not check_user_role(current_user, "admin"):
        membership = db.query(OrganizationMember).filter(
            and_(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == current_user.id,
                OrganizationMember.is_active == True
            )
        ).first()
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this organization"
            )
    
    organization = db.query(Organization).filter(
        and_(
            Organization.id == organization_id,
            Organization.is_active == True
        )
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    return organization

@router.put("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    organization_id: int,
    organization_update: OrganizationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an organization.
    
    - Only organization owners or admins can update
    """
    # Check permissions
    if not check_user_role(current_user, "admin"):
        membership = db.query(OrganizationMember).filter(
            and_(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == current_user.id,
                OrganizationMember.role.in_(["owner", "admin"]),
                OrganizationMember.is_active == True
            )
        ).first()
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this organization"
            )
    
    organization = db.query(Organization).filter(
        and_(
            Organization.id == organization_id,
            Organization.is_active == True
        )
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Update fields
    update_data = organization_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(organization, field, value)
    
    organization.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(organization)
    
    return organization

@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    organization_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete an organization (soft delete).
    
    - Only organization owners or system admins can delete
    """
    # Check permissions
    if not check_user_role(current_user, "admin"):
        membership = db.query(OrganizationMember).filter(
            and_(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == current_user.id,
                OrganizationMember.role == "owner",
                OrganizationMember.is_active == True
            )
        ).first()
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only organization owners can delete organizations"
            )
    
    organization = db.query(Organization).filter(
        and_(
            Organization.id == organization_id,
            Organization.is_active == True
        )
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    organization.is_active = False
    organization.updated_at = datetime.utcnow()
    
    db.commit()

# Organization Member Management

@router.get("/{organization_id}/members", response_model=List[OrganizationMemberResponse])
async def get_organization_members(
    organization_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[str] = Query(None, description="Filter by member role"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get members of an organization."""
    # Check if user has access to this organization
    if not check_user_role(current_user, "admin"):
        membership = db.query(OrganizationMember).filter(
            and_(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == current_user.id,
                OrganizationMember.is_active == True
            )
        ).first()
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this organization"
            )
    
    query = db.query(OrganizationMember).filter(
        and_(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.is_active == True
        )
    )
    
    if role:
        query = query.filter(OrganizationMember.role == role)
    
    members = query.order_by(OrganizationMember.joined_at).offset(skip).limit(limit).all()
    
    return members

@router.post("/{organization_id}/members", response_model=OrganizationMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_organization_member(
    organization_id: int,
    user_id: int,
    role: str = "member",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add a member to an organization.
    
    - Only organization owners/admins can add members
    - Validates that the user exists
    """
    # Check permissions
    if not check_user_role(current_user, "admin"):
        membership = db.query(OrganizationMember).filter(
            and_(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == current_user.id,
                OrganizationMember.role.in_(["owner", "admin"]),
                OrganizationMember.is_active == True
            )
        ).first()
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to add members to this organization"
            )
    
    # Verify organization exists
    organization = db.query(Organization).filter(
        and_(
            Organization.id == organization_id,
            Organization.is_active == True
        )
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is already a member
    existing_membership = db.query(OrganizationMember).filter(
        and_(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user_id
        )
    ).first()
    
    if existing_membership:
        if existing_membership.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this organization"
            )
        else:
            # Reactivate membership
            existing_membership.is_active = True
            existing_membership.role = role
            existing_membership.joined_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_membership)
            return existing_membership
    
    # Create new membership
    new_membership = OrganizationMember(
        organization_id=organization_id,
        user_id=user_id,
        role=role,
        is_active=True
    )
    
    db.add(new_membership)
    db.commit()
    db.refresh(new_membership)
    
    return new_membership

@router.put("/{organization_id}/members/{user_id}", response_model=OrganizationMemberResponse)
async def update_organization_member(
    organization_id: int,
    user_id: int,
    member_update: OrganizationMemberUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an organization member's role or status."""
    # Check permissions
    if not check_user_role(current_user, "admin"):
        membership = db.query(OrganizationMember).filter(
            and_(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == current_user.id,
                OrganizationMember.role.in_(["owner", "admin"]),
                OrganizationMember.is_active == True
            )
        ).first()
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update members in this organization"
            )
    
    member = db.query(OrganizationMember).filter(
        and_(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user_id
        )
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    # Update fields
    update_data = member_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(member, field, value)
    
    db.commit()
    db.refresh(member)
    
    return member

@router.delete("/{organization_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_organization_member(
    organization_id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove a member from an organization."""
    # Check permissions (owners/admins can remove others, users can remove themselves)
    if user_id != current_user.id and not check_user_role(current_user, "admin"):
        membership = db.query(OrganizationMember).filter(
            and_(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == current_user.id,
                OrganizationMember.role.in_(["owner", "admin"]),
                OrganizationMember.is_active == True
            )
        ).first()
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to remove members from this organization"
            )
    
    member = db.query(OrganizationMember).filter(
        and_(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user_id,
            OrganizationMember.is_active == True
        )
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    member.is_active = False
    db.commit()

# API Key Management

@router.post("/{organization_id}/api-keys", response_model=ApiKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    organization_id: int,
    api_key: ApiKeyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create an API key for an organization.
    
    - Only organization owners/admins can create API keys
    - API keys are used for programmatic access
    """
    # Check permissions
    if not check_user_role(current_user, "admin"):
        membership = db.query(OrganizationMember).filter(
            and_(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == current_user.id,
                OrganizationMember.role.in_(["owner", "admin"]),
                OrganizationMember.is_active == True
            )
        ).first()
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to create API keys for this organization"
            )
    
    # Verify organization exists
    organization = db.query(Organization).filter(
        and_(
            Organization.id == organization_id,
            Organization.is_active == True
        )
    ).first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Generate API key
    import secrets
    key_value = f"mk_{secrets.token_urlsafe(32)}"
    
    db_api_key = ApiKey(
        organization_id=organization_id,
        name=api_key.name,
        key_value=key_value,
        permissions=api_key.permissions,
        expires_at=api_key.expires_at,
        is_active=True
    )
    
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    
    return db_api_key

@router.get("/{organization_id}/api-keys", response_model=List[ApiKeyResponse])
async def get_api_keys(
    organization_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get API keys for an organization."""
    # Check permissions
    if not check_user_role(current_user, "admin"):
        membership = db.query(OrganizationMember).filter(
            and_(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == current_user.id,
                OrganizationMember.role.in_(["owner", "admin"]),
                OrganizationMember.is_active == True
            )
        ).first()
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view API keys for this organization"
            )
    
    api_keys = db.query(ApiKey).filter(
        and_(
            ApiKey.organization_id == organization_id,
            ApiKey.is_active == True
        )
    ).order_by(desc(ApiKey.created_at)).all()
    
    return api_keys

@router.delete("/{organization_id}/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    organization_id: int,
    key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Revoke an API key."""
    # Check permissions
    if not check_user_role(current_user, "admin"):
        membership = db.query(OrganizationMember).filter(
            and_(
                OrganizationMember.organization_id == organization_id,
                OrganizationMember.user_id == current_user.id,
                OrganizationMember.role.in_(["owner", "admin"]),
                OrganizationMember.is_active == True
            )
        ).first()
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to revoke API keys for this organization"
            )
    
    api_key = db.query(ApiKey).filter(
        and_(
            ApiKey.id == key_id,
            ApiKey.organization_id == organization_id,
            ApiKey.is_active == True
        )
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    api_key.is_active = False
    api_key.updated_at = datetime.utcnow()
    
    db.commit()

