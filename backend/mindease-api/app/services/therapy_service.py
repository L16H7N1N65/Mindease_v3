"""
Therapy service for managing therapy sessions and exercises.
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db.models.therapy import TherapyExercise, TherapyProgram, TherapySession
from app.db.models.auth import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TherapyService:
    """Service for therapy session and exercise management."""
    
    def __init__(self, db: Session):
        """
        Initialize the therapy service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def get_user_sessions(self, user_id: int, limit: int = 10) -> List[TherapySession]:
        """
        Get therapy sessions for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of sessions to return
            
        Returns:
            List of therapy sessions
        """
        try:
            return self.db.query(TherapySession).filter(
                TherapySession.user_id == user_id
            ).order_by(desc(TherapySession.created_at)).limit(limit).all()
        
        except Exception as e:
            logger.error(f"Error getting user sessions: {str(e)}")
            return []
    
    def create_session(
        self,
        user_id: int,
        exercise_id: int,
        duration: int,
        notes: Optional[str] = None
    ) -> Optional[TherapySession]:
        """
        Create a new therapy session.
        
        Args:
            user_id: User ID
            exercise_id: Exercise ID
            duration: Session duration in seconds
            notes: Optional session notes
            
        Returns:
            Created therapy session or None if creation fails
        """
        try:
            # Check if exercise exists
            exercise = self.db.query(TherapyExercise).filter(
                TherapyExercise.id == exercise_id
            ).first()
            if not exercise:
                logger.error(f"Exercise with ID {exercise_id} not found")
                return None
            
            # Create session
            session = TherapySession(
                user_id=user_id,
                exercise_id=exercise_id,
                duration=duration,
                notes=notes,
                completed=True,
                completed_at=datetime.utcnow()
            )
            self.db.add(session)
            self.db.commit()
            return session
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating therapy session: {str(e)}")
            return None
    
    def get_available_exercises(self) -> List[TherapyExercise]:
        """
        Get all available therapy exercises.
        
        Returns:
            List of therapy exercises
        """
        try:
            return self.db.query(TherapyExercise).all()
        
        except Exception as e:
            logger.error(f"Error getting available exercises: {str(e)}")
            return []
    
    def get_user_programs(self, user_id: int) -> List[TherapyProgram]:
        """
        Get therapy programs for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of therapy programs
        """
        try:
            return self.db.query(TherapyProgram).filter(
                TherapyProgram.user_id == user_id
            ).order_by(desc(TherapyProgram.created_at)).all()
        
        except Exception as e:
            logger.error(f"Error getting user programs: {str(e)}")
            return []
    
    def create_program(
        self,
        user_id: int,
        name: str,
        description: Optional[str] = None,
        exercise_ids: Optional[List[int]] = None
    ) -> Optional[TherapyProgram]:
        """
        Create a new therapy program.
        
        Args:
            user_id: User ID
            name: Program name
            description: Optional program description
            exercise_ids: Optional list of exercise IDs
            
        Returns:
            Created therapy program or None if creation fails
        """
        try:
            # Create program
            program = TherapyProgram(
                user_id=user_id,
                name=name,
                description=description
            )
            self.db.add(program)
            self.db.flush()  # Get program ID
            
            # Add exercises if provided
            if exercise_ids:
                for exercise_id in exercise_ids:
                    exercise = self.db.query(TherapyExercise).filter(
                        TherapyExercise.id == exercise_id
                    ).first()
                    if exercise:
                        program.exercises.append(exercise)
            
            self.db.commit()
            return program
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating therapy program: {str(e)}")
            return None
    
    def get_session_stats(self, user_id: int) -> Dict:
        """
        Get therapy session statistics for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with session statistics
        """
        try:
            # Get total sessions
            total_sessions = self.db.query(TherapySession).filter(
                TherapySession.user_id == user_id
            ).count()
            
            # Get total duration
            total_duration = self.db.query(
                func.sum(TherapySession.duration)
            ).filter(
                TherapySession.user_id == user_id
            ).scalar() or 0
            
            # Get exercise distribution
            exercise_counts = {}
            sessions = self.db.query(
                TherapySession.exercise_id,
                func.count(TherapySession.id)
            ).filter(
                TherapySession.user_id == user_id
            ).group_by(TherapySession.exercise_id).all()
            
            for exercise_id, count in sessions:
                exercise = self.db.query(TherapyExercise).filter(
                    TherapyExercise.id == exercise_id
                ).first()
                if exercise:
                    exercise_counts[exercise.name] = count
            
            return {
                "total_sessions": total_sessions,
                "total_duration": total_duration,
                "exercise_distribution": exercise_counts
            }
        
        except Exception as e:
            logger.error(f"Error getting session stats: {str(e)}")
            return {
                "total_sessions": 0,
                "total_duration": 0,
                "exercise_distribution": {}
            }
