"""
RAG Feedback Service

Business logic for handling user feedback on RAG responses,
analytics processing, and continuous improvement mechanisms.
"""
import json
import csv
import io
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from uuid import UUID
import statistics
import logging

from app.db.models.auth import User
from app.db.models.rag_feedback import RAGFeedback, FeedbackAnalytics, FeedbackTrainingData, ResponseImprovement
from app.schemas.rag_feedback import (
    RAGFeedbackCreate, RAGFeedbackResponse, FeedbackAnalyticsResponse,
    FeedbackSummary, ResponseImprovementCreate, FeedbackTrends,
    CategoryPerformance, UserFeedbackHistory
)

logger = logging.getLogger(__name__)


class RAGFeedbackService:
    """Service for managing RAG feedback and analytics."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_feedback(
        self,
        feedback_data: RAGFeedbackCreate,
        user_id: UUID
    ) -> RAGFeedbackResponse:
        """Create a new feedback record."""
        
        # Create feedback record
        feedback = RAGFeedback(
            user_id=user_id,
            user_query=feedback_data.user_query,
            rag_response=feedback_data.rag_response,
            conversation_id=feedback_data.conversation_id,
            message_id=feedback_data.message_id,
            relevance_score=feedback_data.relevance_score,
            helpfulness_score=feedback_data.helpfulness_score,
            accuracy_score=feedback_data.accuracy_score,
            clarity_score=feedback_data.clarity_score,
            overall_rating=feedback_data.overall_rating,
            feedback_text=feedback_data.feedback_text,
            feedback_category=feedback_data.feedback_category,
            is_helpful=feedback_data.is_helpful,
            is_accurate=feedback_data.is_accurate,
            is_safe=feedback_data.is_safe,
            is_empathetic=feedback_data.is_empathetic,
            suggested_improvement=feedback_data.suggested_improvement,
            missing_information=feedback_data.missing_information,
            query_intent=feedback_data.query_intent,
            user_emotional_state=feedback_data.user_emotional_state,
            session_context=feedback_data.session_context
        )
        
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        
        logger.info(f"Created feedback record {feedback.id} for user {user_id}")
        
        return RAGFeedbackResponse.from_orm(feedback)
    
    async def get_user_feedback(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[RAGFeedbackResponse]:
        """Get feedback history for a specific user."""
        
        feedback_records = self.db.query(RAGFeedback)\
            .filter(RAGFeedback.user_id == user_id)\
            .order_by(desc(RAGFeedback.created_at))\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        return [RAGFeedbackResponse.from_orm(record) for record in feedback_records]
    
    async def get_feedback_summary(
        self,
        organization_id: Optional[UUID] = None,
        days: int = 30
    ) -> FeedbackSummary:
        """Get feedback summary statistics."""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Base query
        query = self.db.query(RAGFeedback)\
            .filter(RAGFeedback.created_at >= start_date)
        
        if organization_id:
            query = query.join(User).filter(User.organization_id == organization_id)
        
        feedback_records = query.all()
        
        if not feedback_records:
            return FeedbackSummary(
                total_feedback=0,
                avg_rating=0.0,
                positive_rate=0.0,
                negative_rate=0.0,
                safety_concerns=0,
                recent_feedback_count=0,
                rating_trend="stable",
                top_complaints=[],
                top_suggestions=[]
            )
        
        # Calculate metrics
        total_feedback = len(feedback_records)
        ratings = [r.overall_rating for r in feedback_records if r.overall_rating]
        avg_rating = statistics.mean(ratings) if ratings else 0.0
        
        positive_count = sum(1 for r in feedback_records if r.overall_rating and r.overall_rating >= 4)
        negative_count = sum(1 for r in feedback_records if r.overall_rating and r.overall_rating <= 2)
        
        positive_rate = positive_count / total_feedback if total_feedback > 0 else 0.0
        negative_rate = negative_count / total_feedback if total_feedback > 0 else 0.0
        
        safety_concerns = sum(1 for r in feedback_records if r.is_safe is False)
        
        # Recent trend analysis (last 7 days vs previous 7 days)
        recent_start = datetime.utcnow() - timedelta(days=7)
        recent_feedback = [r for r in feedback_records if r.created_at >= recent_start]
        previous_feedback = [r for r in feedback_records if r.created_at < recent_start]
        
        recent_avg = statistics.mean([r.overall_rating for r in recent_feedback if r.overall_rating]) if recent_feedback else 0
        previous_avg = statistics.mean([r.overall_rating for r in previous_feedback if r.overall_rating]) if previous_feedback else 0
        
        if recent_avg > previous_avg + 0.2:
            rating_trend = "improving"
        elif recent_avg < previous_avg - 0.2:
            rating_trend = "declining"
        else:
            rating_trend = "stable"
        
        # Extract top complaints and suggestions
        complaints = [r.feedback_text for r in feedback_records if r.feedback_text and r.overall_rating and r.overall_rating <= 2]
        suggestions = [r.suggested_improvement for r in feedback_records if r.suggested_improvement]
        
        # Simple keyword extraction (in production, use NLP)
        top_complaints = self._extract_keywords(complaints)[:5]
        top_suggestions = self._extract_keywords(suggestions)[:5]
        
        return FeedbackSummary(
            total_feedback=total_feedback,
            avg_rating=avg_rating,
            positive_rate=positive_rate,
            negative_rate=negative_rate,
            safety_concerns=safety_concerns,
            recent_feedback_count=len(recent_feedback),
            rating_trend=rating_trend,
            top_complaints=top_complaints,
            top_suggestions=top_suggestions
        )
    
    async def get_feedback_analytics(
        self,
        period_type: str = "daily",
        days: int = 30,
        organization_id: Optional[UUID] = None
    ) -> List[FeedbackAnalyticsResponse]:
        """Get detailed feedback analytics."""
        
        # Check if analytics exist, if not generate them
        start_date = datetime.utcnow() - timedelta(days=days)
        
        analytics_query = self.db.query(FeedbackAnalytics)\
            .filter(
                FeedbackAnalytics.period_type == period_type,
                FeedbackAnalytics.period_start >= start_date
            )\
            .order_by(FeedbackAnalytics.period_start)
        
        analytics_records = analytics_query.all()
        
        # If no analytics exist, generate them
        if not analytics_records:
            await self._generate_analytics(period_type, days, organization_id)
            analytics_records = analytics_query.all()
        
        return [FeedbackAnalyticsResponse.from_orm(record) for record in analytics_records]
    
    async def get_feedback_trends(
        self,
        metric: str = "overall_rating",
        days: int = 30,
        organization_id: Optional[UUID] = None
    ) -> FeedbackTrends:
        """Get feedback trends over time."""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get daily aggregated data
        query = self.db.query(
            func.date(RAGFeedback.created_at).label('date'),
            func.avg(getattr(RAGFeedback, metric)).label('avg_value'),
            func.count(RAGFeedback.id).label('count')
        ).filter(RAGFeedback.created_at >= start_date)
        
        if organization_id:
            query = query.join(User).filter(User.organization_id == organization_id)
        
        daily_data = query.group_by(func.date(RAGFeedback.created_at)).all()
        
        # Convert to data points
        data_points = [
            {
                "date": str(point.date),
                "value": float(point.avg_value) if point.avg_value else 0,
                "count": point.count
            }
            for point in daily_data
        ]
        
        # Calculate trend
        values = [point["value"] for point in data_points if point["value"] > 0]
        if len(values) >= 2:
            # Simple linear trend calculation
            x = list(range(len(values)))
            y = values
            n = len(values)
            
            slope = (n * sum(x[i] * y[i] for i in range(n)) - sum(x) * sum(y)) / (n * sum(x[i]**2 for i in range(n)) - sum(x)**2)
            
            if slope > 0.01:
                trend_direction = "up"
            elif slope < -0.01:
                trend_direction = "down"
            else:
                trend_direction = "stable"
            
            trend_strength = min(abs(slope), 1.0)
        else:
            trend_direction = "stable"
            trend_strength = 0.0
        
        return FeedbackTrends(
            period=f"{days} days",
            data_points=data_points,
            trend_direction=trend_direction,
            trend_strength=trend_strength
        )
    
    async def get_category_performance(
        self,
        days: int = 30,
        organization_id: Optional[UUID] = None
    ) -> List[CategoryPerformance]:
        """Get performance metrics by query category."""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = self.db.query(RAGFeedback)\
            .filter(RAGFeedback.created_at >= start_date)
        
        if organization_id:
            query = query.join(User).filter(User.organization_id == organization_id)
        
        feedback_records = query.all()
        
        # Group by query intent
        category_data = {}
        for record in feedback_records:
            category = record.query_intent or "unknown"
            if category not in category_data:
                category_data[category] = []
            category_data[category].append(record)
        
        # Calculate performance for each category
        performance_list = []
        for category, records in category_data.items():
            ratings = [r.overall_rating for r in records if r.overall_rating]
            avg_rating = statistics.mean(ratings) if ratings else 0.0
            
            positive_count = sum(1 for r in records if r.overall_rating and r.overall_rating >= 4)
            positive_rate = positive_count / len(records) if records else 0.0
            
            # Extract common issues (simplified)
            negative_feedback = [r.feedback_text for r in records if r.feedback_text and r.overall_rating and r.overall_rating <= 2]
            common_issues = self._extract_keywords(negative_feedback)[:3]
            
            # Extract improvement opportunities
            suggestions = [r.suggested_improvement for r in records if r.suggested_improvement]
            improvement_opportunities = self._extract_keywords(suggestions)[:3]
            
            performance_list.append(CategoryPerformance(
                category=category,
                feedback_count=len(records),
                avg_rating=avg_rating,
                positive_rate=positive_rate,
                common_issues=common_issues,
                improvement_opportunities=improvement_opportunities
            ))
        
        return sorted(performance_list, key=lambda x: x.feedback_count, reverse=True)
    
    async def get_filtered_feedback(
        self,
        organization_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        min_rating: Optional[int] = None,
        max_rating: Optional[int] = None,
        query_intent: Optional[str] = None,
        safety_concerns_only: bool = False
    ) -> List[RAGFeedbackResponse]:
        """Get filtered feedback records."""
        
        query = self.db.query(RAGFeedback)
        
        if organization_id:
            query = query.join(User).filter(User.organization_id == organization_id)
        
        if category:
            query = query.filter(RAGFeedback.feedback_category == category)
        
        if min_rating:
            query = query.filter(RAGFeedback.overall_rating >= min_rating)
        
        if max_rating:
            query = query.filter(RAGFeedback.overall_rating <= max_rating)
        
        if query_intent:
            query = query.filter(RAGFeedback.query_intent == query_intent)
        
        if safety_concerns_only:
            query = query.filter(RAGFeedback.is_safe == False)
        
        feedback_records = query.order_by(desc(RAGFeedback.created_at))\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        return [RAGFeedbackResponse.from_orm(record) for record in feedback_records]
    
    async def get_user_feedback_history(
        self,
        user_id: UUID,
        organization_id: Optional[UUID] = None
    ) -> UserFeedbackHistory:
        """Get detailed feedback history for a user."""
        
        query = self.db.query(RAGFeedback).filter(RAGFeedback.user_id == user_id)
        
        if organization_id:
            query = query.join(User).filter(User.organization_id == organization_id)
        
        all_feedback = query.all()
        recent_feedback = query.order_by(desc(RAGFeedback.created_at)).limit(10).all()
        
        if not all_feedback:
            return UserFeedbackHistory(
                user_id=str(user_id),
                total_feedback_given=0,
                avg_rating_given=0.0,
                feedback_frequency="low",
                recent_feedback=[],
                preferred_query_types=[],
                common_emotional_states=[],
                feedback_quality="minimal"
            )
        
        # Calculate metrics
        ratings = [f.overall_rating for f in all_feedback if f.overall_rating]
        avg_rating = statistics.mean(ratings) if ratings else 0.0
        
        # Determine feedback frequency
        days_active = (datetime.utcnow() - min(f.created_at for f in all_feedback)).days
        feedback_per_day = len(all_feedback) / max(days_active, 1)
        
        if feedback_per_day > 1:
            frequency = "high"
        elif feedback_per_day > 0.2:
            frequency = "medium"
        else:
            frequency = "low"
        
        # Extract patterns
        query_types = [f.query_intent for f in all_feedback if f.query_intent]
        emotional_states = [f.user_emotional_state for f in all_feedback if f.user_emotional_state]
        
        preferred_query_types = list(set(query_types))[:5]
        common_emotional_states = list(set(emotional_states))[:5]
        
        # Determine feedback quality
        detailed_feedback_count = sum(1 for f in all_feedback if f.feedback_text)
        quality_ratio = detailed_feedback_count / len(all_feedback)
        
        if quality_ratio > 0.7:
            feedback_quality = "detailed"
        elif quality_ratio > 0.3:
            feedback_quality = "basic"
        else:
            feedback_quality = "minimal"
        
        return UserFeedbackHistory(
            user_id=str(user_id),
            total_feedback_given=len(all_feedback),
            avg_rating_given=avg_rating,
            feedback_frequency=frequency,
            recent_feedback=[RAGFeedbackResponse.from_orm(f) for f in recent_feedback],
            preferred_query_types=preferred_query_types,
            common_emotional_states=common_emotional_states,
            feedback_quality=feedback_quality
        )
    
    async def create_improvement(
        self,
        improvement_data: ResponseImprovementCreate,
        implemented_by: UUID
    ) -> ResponseImprovement:
        """Create a response improvement record."""
        
        improvement = ResponseImprovement(
            feedback_id=improvement_data.feedback_id,
            improvement_type=improvement_data.improvement_type,
            improvement_description=improvement_data.improvement_description,
            implemented_by=implemented_by,
            before_metrics=improvement_data.before_metrics,
            status="planned"
        )
        
        self.db.add(improvement)
        self.db.commit()
        self.db.refresh(improvement)
        
        logger.info(f"Created improvement record {improvement.id}")
        
        return improvement
    
    async def get_improvements(
        self,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        improvement_type: Optional[str] = None,
        organization_id: Optional[UUID] = None
    ) -> List[ResponseImprovement]:
        """Get response improvements with filtering."""
        
        query = self.db.query(ResponseImprovement)
        
        if status:
            query = query.filter(ResponseImprovement.status == status)
        
        if improvement_type:
            query = query.filter(ResponseImprovement.improvement_type == improvement_type)
        
        if organization_id:
            query = query.join(RAGFeedback).join(User)\
                .filter(User.organization_id == organization_id)
        
        improvements = query.order_by(desc(ResponseImprovement.created_at))\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        return improvements
    
    async def update_improvement_status(
        self,
        improvement_id: UUID,
        status: str,
        after_metrics: Optional[Dict[str, Any]] = None
    ) -> ResponseImprovement:
        """Update improvement status and metrics."""
        
        improvement = self.db.query(ResponseImprovement)\
            .filter(ResponseImprovement.id == improvement_id)\
            .first()
        
        if not improvement:
            raise ValueError(f"Improvement {improvement_id} not found")
        
        improvement.status = status
        if after_metrics:
            improvement.after_metrics = after_metrics
            
            # Calculate impact score if both before and after metrics exist
            if improvement.before_metrics:
                improvement.impact_score = self._calculate_impact_score(
                    improvement.before_metrics,
                    after_metrics
                )
        
        self.db.commit()
        self.db.refresh(improvement)
        
        return improvement
    
    async def process_feedback_analytics(self, feedback_id: UUID):
        """Process feedback for analytics (background task)."""
        
        feedback = self.db.query(RAGFeedback)\
            .filter(RAGFeedback.id == feedback_id)\
            .first()
        
        if not feedback:
            return
        
        # Update daily analytics
        today = datetime.utcnow().date()
        analytics = self.db.query(FeedbackAnalytics)\
            .filter(
                FeedbackAnalytics.period_type == "daily",
                func.date(FeedbackAnalytics.period_start) == today
            ).first()
        
        if not analytics:
            analytics = FeedbackAnalytics(
                period_start=datetime.combine(today, datetime.min.time()),
                period_end=datetime.combine(today, datetime.max.time()),
                period_type="daily",
                total_feedback_count=0
            )
            self.db.add(analytics)
        
        # Update analytics with new feedback
        analytics.total_feedback_count += 1
        
        # Recalculate averages (simplified - in production, use incremental updates)
        daily_feedback = self.db.query(RAGFeedback)\
            .filter(func.date(RAGFeedback.created_at) == today)\
            .all()
        
        if daily_feedback:
            ratings = [f.overall_rating for f in daily_feedback if f.overall_rating]
            if ratings:
                analytics.avg_overall_rating = statistics.mean(ratings)
            
            relevance_scores = [f.relevance_score for f in daily_feedback if f.relevance_score]
            if relevance_scores:
                analytics.avg_relevance_score = statistics.mean(relevance_scores)
        
        self.db.commit()
        
        logger.info(f"Updated analytics for feedback {feedback_id}")
    
    async def handle_safety_concern(self, feedback_id: UUID):
        """Handle safety concerns (background task)."""
        
        feedback = self.db.query(RAGFeedback)\
            .filter(RAGFeedback.id == feedback_id)\
            .first()
        
        if not feedback or feedback.is_safe is not False:
            return
        
        # Log safety concern
        logger.warning(f"Safety concern reported for feedback {feedback_id}: {feedback.feedback_text}")
        
        # In production, this would:
        # 1. Alert administrators
        # 2. Flag the response for review
        # 3. Potentially disable similar responses
        # 4. Create improvement tasks
        
        # Create automatic improvement task
        improvement = ResponseImprovement(
            feedback_id=feedback_id,
            improvement_type="safety_enhancement",
            improvement_description=f"Address safety concern: {feedback.feedback_text}",
            status="planned"
        )
        
        self.db.add(improvement)
        self.db.commit()
        
        logger.info(f"Created safety improvement task for feedback {feedback_id}")
    
    async def export_feedback(
        self,
        organization_id: Optional[UUID] = None,
        format: str = "csv",
        days: int = 30,
        include_text: bool = True
    ) -> str:
        """Export feedback data for analysis."""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = self.db.query(RAGFeedback)\
            .filter(RAGFeedback.created_at >= start_date)
        
        if organization_id:
            query = query.join(User).filter(User.organization_id == organization_id)
        
        feedback_records = query.all()
        
        if format == "csv":
            return self._export_to_csv(feedback_records, include_text)
        elif format == "json":
            return self._export_to_json(feedback_records, include_text)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    async def generate_training_data(
        self,
        organization_id: Optional[UUID] = None,
        min_feedback_count: int = 10,
        quality_threshold: float = 0.7
    ):
        """Generate training data from feedback (background task)."""
        
        # Get feedback with sufficient data
        query = self.db.query(RAGFeedback)\
            .filter(RAGFeedback.overall_rating.isnot(None))
        
        if organization_id:
            query = query.join(User).filter(User.organization_id == organization_id)
        
        feedback_records = query.all()
        
        if len(feedback_records) < min_feedback_count:
            logger.warning(f"Insufficient feedback data: {len(feedback_records)} < {min_feedback_count}")
            return
        
        # Process feedback into training data
        training_count = 0
        for feedback in feedback_records:
            # Calculate quality score
            quality_score = self._calculate_feedback_quality(feedback)
            
            if quality_score >= quality_threshold:
                # Create training data record
                training_data = FeedbackTrainingData(
                    feedback_id=feedback.id,
                    query_length=len(feedback.user_query),
                    response_length=len(feedback.rag_response),
                    quality_label="high" if feedback.overall_rating >= 4 else "low",
                    binary_label=feedback.overall_rating >= 4,
                    regression_target=feedback.overall_rating / 5.0,
                    data_quality="high" if quality_score >= 0.8 else "medium",
                    training_set="train"  # Would implement train/val/test split
                )
                
                self.db.add(training_data)
                training_count += 1
        
        self.db.commit()
        
        logger.info(f"Generated {training_count} training data records")
    
    # Helper methods
    
    def _extract_keywords(self, texts: List[str]) -> List[str]:
        """Simple keyword extraction (in production, use NLP)."""
        if not texts:
            return []
        
        # Simple word frequency analysis
        word_counts = {}
        for text in texts:
            words = text.lower().split()
            for word in words:
                if len(word) > 3:  # Filter short words
                    word_counts[word] = word_counts.get(word, 0) + 1
        
        # Return top words
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_words[:10]]
    
    def _calculate_impact_score(
        self,
        before_metrics: Dict[str, Any],
        after_metrics: Dict[str, Any]
    ) -> float:
        """Calculate improvement impact score."""
        
        # Simple improvement calculation
        # In production, this would be more sophisticated
        
        before_rating = before_metrics.get("avg_rating", 0)
        after_rating = after_metrics.get("avg_rating", 0)
        
        if before_rating > 0:
            improvement = (after_rating - before_rating) / before_rating
            return max(0, min(1, improvement))  # Normalize to 0-1
        
        return 0.0
    
    def _calculate_feedback_quality(self, feedback: RAGFeedback) -> float:
        """Calculate quality score for feedback."""
        
        score = 0.0
        
        # Has overall rating
        if feedback.overall_rating:
            score += 0.2
        
        # Has detailed scores
        if feedback.relevance_score:
            score += 0.1
        if feedback.helpfulness_score:
            score += 0.1
        if feedback.accuracy_score:
            score += 0.1
        if feedback.clarity_score:
            score += 0.1
        
        # Has text feedback
        if feedback.feedback_text and len(feedback.feedback_text) > 10:
            score += 0.2
        
        # Has suggestions
        if feedback.suggested_improvement:
            score += 0.1
        
        # Has context
        if feedback.query_intent:
            score += 0.05
        if feedback.user_emotional_state:
            score += 0.05
        
        return score
    
    def _export_to_csv(self, feedback_records: List[RAGFeedback], include_text: bool) -> str:
        """Export feedback to CSV format."""
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers
        headers = [
            "id", "user_id", "created_at", "overall_rating",
            "relevance_score", "helpfulness_score", "accuracy_score", "clarity_score",
            "is_helpful", "is_accurate", "is_safe", "is_empathetic",
            "query_intent", "user_emotional_state", "feedback_category"
        ]
        
        if include_text:
            headers.extend(["user_query", "rag_response", "feedback_text", "suggested_improvement"])
        
        writer.writerow(headers)
        
        # Data rows
        for feedback in feedback_records:
            row = [
                str(feedback.id), str(feedback.user_id), feedback.created_at.isoformat(),
                feedback.overall_rating, feedback.relevance_score, feedback.helpfulness_score,
                feedback.accuracy_score, feedback.clarity_score,
                feedback.is_helpful, feedback.is_accurate, feedback.is_safe, feedback.is_empathetic,
                feedback.query_intent, feedback.user_emotional_state, feedback.feedback_category
            ]
            
            if include_text:
                row.extend([
                    feedback.user_query, feedback.rag_response,
                    feedback.feedback_text, feedback.suggested_improvement
                ])
            
            writer.writerow(row)
        
        return output.getvalue()
    
    def _export_to_json(self, feedback_records: List[RAGFeedback], include_text: bool) -> str:
        """Export feedback to JSON format."""
        
        data = []
        for feedback in feedback_records:
            record = {
                "id": str(feedback.id),
                "user_id": str(feedback.user_id),
                "created_at": feedback.created_at.isoformat(),
                "overall_rating": feedback.overall_rating,
                "relevance_score": feedback.relevance_score,
                "helpfulness_score": feedback.helpfulness_score,
                "accuracy_score": feedback.accuracy_score,
                "clarity_score": feedback.clarity_score,
                "is_helpful": feedback.is_helpful,
                "is_accurate": feedback.is_accurate,
                "is_safe": feedback.is_safe,
                "is_empathetic": feedback.is_empathetic,
                "query_intent": feedback.query_intent,
                "user_emotional_state": feedback.user_emotional_state,
                "feedback_category": feedback.feedback_category
            }
            
            if include_text:
                record.update({
                    "user_query": feedback.user_query,
                    "rag_response": feedback.rag_response,
                    "feedback_text": feedback.feedback_text,
                    "suggested_improvement": feedback.suggested_improvement
                })
            
            data.append(record)
        
        return json.dumps(data, indent=2)
    
    async def _generate_analytics(
        self,
        period_type: str,
        days: int,
        organization_id: Optional[UUID] = None
    ):
        """Generate missing analytics records."""
        
        # This would generate analytics for missing periods
        # Simplified implementation for demo
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        if period_type == "daily":
            current_date = start_date.date()
            end_date = datetime.utcnow().date()
            
            while current_date <= end_date:
                # Check if analytics exist for this day
                existing = self.db.query(FeedbackAnalytics)\
                    .filter(
                        FeedbackAnalytics.period_type == "daily",
                        func.date(FeedbackAnalytics.period_start) == current_date
                    ).first()
                
                if not existing:
                    # Create analytics for this day
                    day_start = datetime.combine(current_date, datetime.min.time())
                    day_end = datetime.combine(current_date, datetime.max.time())
                    
                    # Get feedback for this day
                    query = self.db.query(RAGFeedback)\
                        .filter(
                            RAGFeedback.created_at >= day_start,
                            RAGFeedback.created_at <= day_end
                        )
                    
                    if organization_id:
                        query = query.join(User).filter(User.organization_id == organization_id)
                    
                    daily_feedback = query.all()
                    
                    # Calculate metrics
                    analytics = FeedbackAnalytics(
                        period_start=day_start,
                        period_end=day_end,
                        period_type="daily",
                        total_feedback_count=len(daily_feedback)
                    )
                    
                    if daily_feedback:
                        ratings = [f.overall_rating for f in daily_feedback if f.overall_rating]
                        if ratings:
                            analytics.avg_overall_rating = statistics.mean(ratings)
                    
                    self.db.add(analytics)
                
                current_date += timedelta(days=1)
            
            self.db.commit()

