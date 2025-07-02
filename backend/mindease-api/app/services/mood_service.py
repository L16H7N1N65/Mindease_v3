"""
Mood service for managing mood tracking and analytics.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.db.models.mood import MoodEntry, MoodFactor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MoodService:
    """Service for mood tracking and analytics."""
    
    def __init__(self, db: Session):
        """
        Initialize the mood service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def get_user_mood_entries(
        self, 
        user_id: int, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 30
    ) -> List[MoodEntry]:
        """
        Get mood entries for a user within a date range.
        
        Args:
            user_id: User ID
            start_date: Optional start date
            end_date: Optional end date
            limit: Maximum number of entries to return
            
        Returns:
            List of mood entries
        """
        try:
            query = self.db.query(MoodEntry).filter(MoodEntry.user_id == user_id)
            
            if start_date:
                query = query.filter(MoodEntry.created_at >= start_date)
            
            if end_date:
                query = query.filter(MoodEntry.created_at <= end_date)
            
            return query.order_by(desc(MoodEntry.created_at)).limit(limit).all()
        
        except Exception as e:
            logger.error(f"Error getting user mood entries: {str(e)}")
            return []
    
    def create_mood_entry(
        self,
        user_id: int,
        mood_value: int,
        notes: Optional[str] = None,
        factors: Optional[List[Dict]] = None
    ) -> Optional[MoodEntry]:
        """
        Create a new mood entry.
        
        Args:
            user_id: User ID
            mood_value: Mood value (1-10)
            notes: Optional notes
            factors: Optional list of mood factors (dicts with name and impact)
            
        Returns:
            Created mood entry or None if creation fails
        """
        try:
            # Validate mood value
            if not 1 <= mood_value <= 10:
                logger.error(f"Invalid mood value: {mood_value}")
                return None
            
            # Create mood entry
            entry = MoodEntry(
                user_id=user_id,
                value=mood_value,
                notes=notes
            )
            self.db.add(entry)
            self.db.flush()  # Get entry ID
            
            # Add factors if provided
            if factors:
                for factor_data in factors:
                    factor = MoodFactor(
                        entry_id=entry.id,
                        name=factor_data.get("name"),
                        impact=factor_data.get("impact", 0)
                    )
                    self.db.add(factor)
            
            self.db.commit()
            return entry
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating mood entry: {str(e)}")
            return None
    
    def get_mood_trends(
        self, 
        user_id: int, 
        days: int = 30
    ) -> Dict:
        """
        Get mood trends for a user over a period of days.
        
        Args:
            user_id: User ID
            days: Number of days to analyze
            
        Returns:
            Dictionary with mood trends
        """
        try:
            # Calculate start date
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get mood entries
            entries = self.db.query(MoodEntry).filter(
                MoodEntry.user_id == user_id,
                MoodEntry.created_at >= start_date
            ).order_by(MoodEntry.created_at).all()
            
            # Calculate average mood
            if entries:
                average_mood = sum(entry.value for entry in entries) / len(entries)
            else:
                average_mood = 0
            
            # Calculate mood by day of week
            mood_by_day = {}
            for entry in entries:
                day_of_week = entry.created_at.strftime("%A")
                if day_of_week not in mood_by_day:
                    mood_by_day[day_of_week] = {"total": 0, "count": 0}
                mood_by_day[day_of_week]["total"] += entry.value
                mood_by_day[day_of_week]["count"] += 1
            
            for day, data in mood_by_day.items():
                mood_by_day[day]["average"] = data["total"] / data["count"]
            
            # Get common factors
            factor_counts = {}
            for entry in entries:
                for factor in entry.factors:
                    if factor.name not in factor_counts:
                        factor_counts[factor.name] = {"positive": 0, "negative": 0, "neutral": 0}
                    
                    if factor.impact > 0:
                        factor_counts[factor.name]["positive"] += 1
                    elif factor.impact < 0:
                        factor_counts[factor.name]["negative"] += 1
                    else:
                        factor_counts[factor.name]["neutral"] += 1
            
            # Sort factors by total count
            sorted_factors = sorted(
                factor_counts.items(),
                key=lambda x: x[1]["positive"] + x[1]["negative"] + x[1]["neutral"],
                reverse=True
            )
            top_factors = dict(sorted_factors[:5])
            
            return {
                "average_mood": average_mood,
                "mood_by_day": mood_by_day,
                "top_factors": top_factors,
                "entry_count": len(entries)
            }
        
        except Exception as e:
            logger.error(f"Error getting mood trends: {str(e)}")
            return {
                "average_mood": 0,
                "mood_by_day": {},
                "top_factors": {},
                "entry_count": 0
            }
    
    def get_mood_factors_summary(self, user_id: int) -> Dict:
        """
        Get a summary of mood factors for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with mood factors summary
        """
        try:
            # Get all factors for user's entries
            factors = self.db.query(MoodFactor).join(
                MoodEntry, MoodFactor.entry_id == MoodEntry.id
            ).filter(
                MoodEntry.user_id == user_id
            ).all()
            
            # Group factors by name
            factor_groups = {}
            for factor in factors:
                if factor.name not in factor_groups:
                    factor_groups[factor.name] = []
                factor_groups[factor.name].append(factor.impact)
            
            # Calculate statistics for each factor
            factor_stats = {}
            for name, impacts in factor_groups.items():
                avg_impact = sum(impacts) / len(impacts)
                factor_stats[name] = {
                    "count": len(impacts),
                    "average_impact": avg_impact,
                    "positive_count": sum(1 for i in impacts if i > 0),
                    "negative_count": sum(1 for i in impacts if i < 0),
                    "neutral_count": sum(1 for i in impacts if i == 0)
                }
            
            # Sort by count
            sorted_stats = sorted(
                factor_stats.items(),
                key=lambda x: x[1]["count"],
                reverse=True
            )
            
            return dict(sorted_stats)
        
        except Exception as e:
            logger.error(f"Error getting mood factors summary: {str(e)}")
            return {}
