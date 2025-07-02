"""
Social service for managing social interactions.
"""
import logging
from typing import Dict, List, Optional, Tuple

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.db.models.social import (
    SocialPost,
    SocialComment,
    SocialLike,
    SocialTag,
    SocialPostTag,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SocialService:
    """Service for social interaction management."""
    
    def __init__(self, db: Session):
        """
        Initialize the social service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def get_posts(
        self,
        limit: int = 20,
        offset: int = 0,
        user_id: Optional[int] = None,
        tag: Optional[str] = None
    ) -> List[SocialPost]:
        """
        Get social posts with optional filtering.
        """
        try:
            query = self.db.query(SocialPost)
            
            if user_id:
                query = query.filter(SocialPost.user_id == user_id)
            
            if tag:
                # --- Old: join(Tag) ---
                # query = query.join(Tag).filter(Tag.name == tag)
                # New: join via the association table SocialPostTag and SocialTag
                query = (
                    query
                    .join(SocialPostTag, SocialPostTag.post_id == SocialPost.id)
                    .join(SocialTag, SocialTag.id == SocialPostTag.tag_id)
                    .filter(SocialTag.name == tag)
                )
            
            return (
                query
                .order_by(desc(SocialPost.created_at))
                .offset(offset)
                .limit(limit)
                .all()
            )
        
        except Exception as e:
            logger.error(f"Error getting posts: {e}")
            return []
    
    def create_post(
        self,
        user_id: int,
        content: str,
        tags: Optional[List[str]] = None
    ) -> Optional[SocialPost]:
        """
        Create a new social post.
        """
        try:
            post = SocialPost(
                user_id=user_id,
                content=content
            )
            self.db.add(post)
            self.db.flush()  # to assign post.id
            
            if tags:
                for tag_name in tags:
                    # --- Old: Tag(...) ---
                    # tag = Tag(name=tag_name.lower().strip())
                    # New: use SocialTag and SocialPostTag
                    tag_obj = (
                        self.db.query(SocialTag)
                              .filter(SocialTag.name == tag_name.lower().strip())
                              .first()
                    )
                    if not tag_obj:
                        tag_obj = SocialTag(name=tag_name.lower().strip())
                        self.db.add(tag_obj)
                        self.db.flush()
                    assoc = SocialPostTag(
                        post_id=post.id,
                        tag_id=tag_obj.id
                    )
                    self.db.add(assoc)
            
            self.db.commit()
            return post
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating post: {e}")
            return None
    
    def add_comment(
        self,
        post_id: int,
        user_id: int,
        content: str
    ) -> Optional[SocialComment]:
        """
        Add a comment to a post.
        """
        try:
            post = self.db.query(SocialPost).get(post_id)
            if not post:
                logger.error(f"Post {post_id} not found")
                return None
            
            # --- Old: Comment(...) ---
            # comment = Comment(post_id=post_id, ...)
            comment = SocialComment(
                post_id=post_id,
                user_id=user_id,
                content=content
            )
            self.db.add(comment)
            self.db.commit()
            return comment
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding comment: {e}")
            return None
    
    def add_like(
        self,
        post_id: Optional[int],
        comment_id: Optional[int],
        user_id: int
    ) -> Optional[SocialLike]:
        """
        Add a like to a post or comment.
        """
        try:
            if post_id:
                target = self.db.query(SocialPost).get(post_id)
            else:
                target = self.db.query(SocialComment).get(comment_id)
            
            if not target:
                logger.error("Target for like not found")
                return None
            
            # --- Old: Like(...) ---
            # existing = self.db.query(Like)...
            existing = (
                self.db.query(SocialLike)
                       .filter(
                           SocialLike.user_id == user_id,
                           SocialLike.post_id == post_id,
                           SocialLike.comment_id == comment_id
                       )
                       .first()
            )
            if existing:
                return existing
            
            like = SocialLike(
                user_id=user_id,
                post_id=post_id,
                comment_id=comment_id
            )
            self.db.add(like)
            self.db.commit()
            return like
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding like: {e}")
            return None
    
    def remove_like(
        self,
        post_id: Optional[int],
        comment_id: Optional[int],
        user_id: int
    ) -> bool:
        """
        Remove a like from a post or comment.
        """
        try:
            like = (
                self.db.query(SocialLike)
                       .filter(
                           SocialLike.user_id == user_id,
                           SocialLike.post_id == post_id,
                           SocialLike.comment_id == comment_id
                       )
                       .first()
            )
            if not like:
                return False
            self.db.delete(like)
            self.db.commit()
            return True
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error removing like: {e}")
            return False
    
    def get_post_with_comments(
        self,
        post_id: int
    ) -> Optional[Tuple[SocialPost, List[SocialComment]]]:
        """
        Get a post with its comments.
        """
        try:
            post = self.db.query(SocialPost).get(post_id)
            if not post:
                return None
            
            # --- Old: Comment(...)---
            # comments = self.db.query(Comment)...
            comments = (
                self.db.query(SocialComment)
                       .filter(SocialComment.post_id == post_id)
                       .order_by(SocialComment.created_at)
                       .all()
            )
            return post, comments
        
        except Exception as e:
            logger.error(f"Error getting post with comments: {e}")
            return None
    
    def get_trending_tags(self, limit: int = 10) -> List[Dict]:
        """
        Get trending tags.
        """
        try:
            # --- Old: Tag.name, func.count(Tag.id) ---
            # tag_counts = self.db.query(Tag.name, ...)
            tag_counts = (
                self.db.query(
                    SocialTag.name,
                    func.count(SocialPostTag.id).label("count")
                )
                .join(SocialPostTag, SocialPostTag.tag_id == SocialTag.id)
                .group_by(SocialTag.name)
                .order_by(desc("count"))
                .limit(limit)
                .all()
            )
            return [{"name": name, "count": count} for name, count in tag_counts]
        
        except Exception as e:
            logger.error(f"Error getting trending tags: {e}")
            return []