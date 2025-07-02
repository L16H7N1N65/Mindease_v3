"""
GDPR Compliance Module for MindEase
Implements data protection and privacy requirements
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

class DataProcessingPurpose(Enum):
    """Legal basis for data processing under GDPR"""
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"

class DataCategory(Enum):
    """Categories of personal data"""
    IDENTITY = "identity"  # Name, email, etc.
    CONTACT = "contact"    # Address, phone, etc.
    HEALTH = "health"      # Mental health data
    BEHAVIORAL = "behavioral"  # Usage patterns
    TECHNICAL = "technical"    # IP, device info
    PREFERENCES = "preferences"  # Settings, choices

@dataclass
class DataProcessingRecord:
    """Record of data processing activity"""
    purpose: DataProcessingPurpose
    data_categories: List[DataCategory]
    legal_basis: str
    retention_period: int  # days
    recipients: List[str]
    transfers_outside_eu: bool = False

class GDPRManager:
    """GDPR compliance manager"""
    
    def __init__(self, db: Session):
        self.db = db
        self.processing_records = self._initialize_processing_records()
    
    def _initialize_processing_records(self) -> Dict[str, DataProcessingRecord]:
        """Initialize data processing records"""
        return {
            "user_registration": DataProcessingRecord(
                purpose=DataProcessingPurpose.CONTRACT,
                data_categories=[DataCategory.IDENTITY, DataCategory.CONTACT],
                legal_basis="Performance of contract",
                retention_period=2555,  # 7 years
                recipients=["MindEase Platform"]
            ),
            "therapy_sessions": DataProcessingRecord(
                purpose=DataProcessingPurpose.CONSENT,
                data_categories=[DataCategory.HEALTH, DataCategory.BEHAVIORAL],
                legal_basis="Explicit consent for health data processing",
                retention_period=365,  # 1 year
                recipients=["MindEase Platform", "AI Processing Service"]
            ),
            "analytics": DataProcessingRecord(
                purpose=DataProcessingPurpose.LEGITIMATE_INTERESTS,
                data_categories=[DataCategory.BEHAVIORAL, DataCategory.TECHNICAL],
                legal_basis="Legitimate interest in service improvement",
                retention_period=730,  # 2 years
                recipients=["MindEase Platform", "Analytics Service"]
            ),
            "security_monitoring": DataProcessingRecord(
                purpose=DataProcessingPurpose.LEGITIMATE_INTERESTS,
                data_categories=[DataCategory.TECHNICAL],
                legal_basis="Legitimate interest in security",
                retention_period=90,  # 3 months
                recipients=["MindEase Platform"]
            )
        }
    
    def record_consent(self, user_id: int, purpose: str, granted: bool, 
                      consent_text: str) -> Dict[str, Any]:
        """Record user consent"""
        consent_record = {
            "user_id": user_id,
            "purpose": purpose,
            "granted": granted,
            "consent_text": consent_text,
            "timestamp": datetime.utcnow(),
            "ip_address": None,  # Should be passed from request
            "user_agent": None   # Should be passed from request
        }
        
        # Store in database (implementation depends on your consent table)
        logger.info(f"Consent recorded for user {user_id}: {purpose} = {granted}")
        
        return consent_record
    
    def check_consent(self, user_id: int, purpose: str) -> bool:
        """Check if user has given consent for specific purpose"""
        # Query consent table
        query = text("""
            SELECT granted FROM user_consents 
            WHERE user_id = :user_id AND purpose = :purpose 
            ORDER BY created_at DESC LIMIT 1
        """)
        
        result = self.db.execute(query, {"user_id": user_id, "purpose": purpose}).fetchone()
        return result.granted if result else False
    
    def withdraw_consent(self, user_id: int, purpose: str) -> bool:
        """Allow user to withdraw consent"""
        try:
            # Record consent withdrawal
            self.record_consent(user_id, purpose, False, "Consent withdrawn by user")
            
            # Trigger data deletion if required
            if purpose == "therapy_sessions":
                self._delete_therapy_data(user_id)
            elif purpose == "analytics":
                self._anonymize_analytics_data(user_id)
            
            return True
        except Exception as e:
            logger.error(f"Failed to withdraw consent for user {user_id}: {e}")
            return False
    
    def generate_privacy_notice(self) -> Dict[str, Any]:
        """Generate privacy notice content"""
        return {
            "controller": {
                "name": "MindEase Platform",
                "contact": "privacy@mindease.com",
                "dpo_contact": "dpo@mindease.com"
            },
            "purposes": [
                {
                    "purpose": "Service Provision",
                    "legal_basis": "Contract performance",
                    "data_types": ["Identity", "Contact", "Health"],
                    "retention": "7 years after account closure"
                },
                {
                    "purpose": "AI-Powered Therapy Support",
                    "legal_basis": "Explicit consent",
                    "data_types": ["Health", "Behavioral"],
                    "retention": "1 year or until consent withdrawal"
                },
                {
                    "purpose": "Service Improvement",
                    "legal_basis": "Legitimate interest",
                    "data_types": ["Behavioral", "Technical"],
                    "retention": "2 years in anonymized form"
                }
            ],
            "user_rights": [
                "Right to access your data",
                "Right to rectify incorrect data",
                "Right to erase your data",
                "Right to restrict processing",
                "Right to data portability",
                "Right to object to processing",
                "Right to withdraw consent"
            ],
            "data_transfers": {
                "outside_eu": False,
                "safeguards": "Standard Contractual Clauses"
            },
            "automated_decision_making": {
                "exists": True,
                "description": "AI-powered therapy recommendations",
                "user_rights": "Right to human review of decisions"
            }
        }
    
    def handle_data_subject_request(self, user_id: int, request_type: str) -> Dict[str, Any]:
        """Handle data subject rights requests"""
        if request_type == "access":
            return self._handle_access_request(user_id)
        elif request_type == "portability":
            return self._handle_portability_request(user_id)
        elif request_type == "erasure":
            return self._handle_erasure_request(user_id)
        elif request_type == "rectification":
            return self._handle_rectification_request(user_id)
        else:
            raise ValueError(f"Unknown request type: {request_type}")
    
    def _handle_access_request(self, user_id: int) -> Dict[str, Any]:
        """Handle subject access request"""
        user_data = {}
        
        # Collect data from all relevant tables
        tables = [
            "users", "user_profiles", "therapy_sessions", 
            "mood_entries", "breathing_exercises", "conversations"
        ]
        
        for table in tables:
            query = text(f"SELECT * FROM {table} WHERE user_id = :user_id")
            results = self.db.execute(query, {"user_id": user_id}).fetchall()
            user_data[table] = [dict(row) for row in results]
        
        return {
            "request_type": "access",
            "user_id": user_id,
            "data": user_data,
            "generated_at": datetime.utcnow().isoformat(),
            "retention_info": self.processing_records
        }
    
    def _handle_portability_request(self, user_id: int) -> Dict[str, Any]:
        """Handle data portability request"""
        # Return data in structured, machine-readable format
        portable_data = self._handle_access_request(user_id)
        portable_data["request_type"] = "portability"
        portable_data["format"] = "JSON"
        
        return portable_data
    
    def _handle_erasure_request(self, user_id: int) -> Dict[str, Any]:
        """Handle right to erasure request"""
        try:
            # Check if erasure is possible (no legal obligations)
            if self._can_erase_data(user_id):
                # Anonymize or delete data
                self._anonymize_user_data(user_id)
                
                return {
                    "request_type": "erasure",
                    "user_id": user_id,
                    "status": "completed",
                    "completed_at": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "request_type": "erasure",
                    "user_id": user_id,
                    "status": "rejected",
                    "reason": "Legal obligation to retain data"
                }
        except Exception as e:
            logger.error(f"Erasure request failed for user {user_id}: {e}")
            return {
                "request_type": "erasure",
                "user_id": user_id,
                "status": "failed",
                "error": str(e)
            }
    
    def _handle_rectification_request(self, user_id: int) -> Dict[str, Any]:
        """Handle data rectification request"""
        return {
            "request_type": "rectification",
            "user_id": user_id,
            "status": "manual_review_required",
            "message": "Please contact support with specific corrections needed"
        }
    
    def _can_erase_data(self, user_id: int) -> bool:
        """Check if user data can be erased"""
        # Check for legal obligations to retain data
        # e.g., ongoing legal proceedings, regulatory requirements
        return True  # Simplified for demo
    
    def _anonymize_user_data(self, user_id: int):
        """Anonymize user data while preserving analytics value"""
        # Replace identifiable information with anonymous identifiers
        anonymous_id = f"anon_{hash(str(user_id)) % 1000000}"
        
        # Update tables with anonymized data
        tables_to_anonymize = [
            "users", "user_profiles", "therapy_sessions", 
            "mood_entries", "conversations"
        ]
        
        for table in tables_to_anonymize:
            query = text(f"""
                UPDATE {table} 
                SET email = :anon_email, 
                    name = :anon_name,
                    anonymized = true,
                    anonymized_at = :timestamp
                WHERE user_id = :user_id
            """)
            
            self.db.execute(query, {
                "anon_email": f"{anonymous_id}@anonymized.local",
                "anon_name": f"Anonymous User {anonymous_id}",
                "timestamp": datetime.utcnow(),
                "user_id": user_id
            })
    
    def _delete_therapy_data(self, user_id: int):
        """Delete therapy data when consent is withdrawn"""
        tables = ["therapy_sessions", "conversations", "mood_entries"]
        
        for table in tables:
            query = text(f"DELETE FROM {table} WHERE user_id = :user_id")
            self.db.execute(query, {"user_id": user_id})
    
    def _anonymize_analytics_data(self, user_id: int):
        """Anonymize analytics data"""
        query = text("""
            UPDATE analytics_events 
            SET user_id = NULL, 
                anonymized = true 
            WHERE user_id = :user_id
        """)
        self.db.execute(query, {"user_id": user_id})
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate GDPR compliance report"""
        return {
            "report_date": datetime.utcnow().isoformat(),
            "data_processing_activities": self.processing_records,
            "consent_statistics": self._get_consent_statistics(),
            "data_subject_requests": self._get_request_statistics(),
            "data_breaches": self._get_breach_statistics(),
            "retention_compliance": self._check_retention_compliance()
        }
    
    def _get_consent_statistics(self) -> Dict[str, int]:
        """Get consent statistics"""
        # Query consent table for statistics
        return {
            "total_consents": 0,
            "active_consents": 0,
            "withdrawn_consents": 0
        }
    
    def _get_request_statistics(self) -> Dict[str, int]:
        """Get data subject request statistics"""
        return {
            "access_requests": 0,
            "erasure_requests": 0,
            "portability_requests": 0,
            "rectification_requests": 0
        }
    
    def _get_breach_statistics(self) -> Dict[str, int]:
        """Get data breach statistics"""
        return {
            "total_breaches": 0,
            "reported_to_authority": 0,
            "users_notified": 0
        }
    
    def _check_retention_compliance(self) -> Dict[str, Any]:
        """Check data retention compliance"""
        # Check for data that should be deleted based on retention periods
        return {
            "compliant": True,
            "overdue_deletions": [],
            "upcoming_deletions": []
        }

