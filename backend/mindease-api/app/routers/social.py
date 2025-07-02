"""
Social features router for posts, comments, likes, and community interaction
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func, or_
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.db.models import (
    User, SocialPost, SocialComment, SocialLike, SocialTag, SocialPostTag
)
from app.schemas.social import (
    SocialPostCreate, SocialPostResponse, SocialPostUpdate,
    SocialCommentCreate, SocialCommentResponse, SocialCommentUpdate,
    SocialTagResponse, SocialFeedResponse
)
from app.core.security import get_current_active_user

# router = APIRouter(
#     prefix="/social",
#     tags=["social"]
# )

router = APIRouter(tags=[("social")])
# Social Post Endpoints

@router.post("/posts", response_model=SocialPostResponse, status_code=status.HTTP_201_CREATED)
async def create_social_post(
    post: SocialPostCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new social post.
    
    - Users can share experiences, tips, or ask for support
    - Posts can be anonymous or attributed
    - Supports tagging for categorization
    """
    db_post = SocialPost(
        user_id=current_user.id,
        title=post.title,
        content=post.content,
        is_anonymous=post.is_anonymous,
        is_active=True
    )
    
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    # Add tags if provided
    if post.tag_ids:
        for tag_id in post.tag_ids:
            # Verify tag exists
            tag = db.query(SocialTag).filter(SocialTag.id == tag_id).first()
            if tag:
                post_tag = SocialPostTag(post_id=db_post.id, tag_id=tag_id)
                db.add(post_tag)
        
        db.commit()
        db.refresh(db_post)
    
    return db_post

@router.get("/posts", response_model=List[SocialPostResponse])
async def get_social_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    tag_id: Optional[int] = Query(None, description="Filter by tag ID"),
    search: Optional[str] = Query(None, description="Search in title and content"),
    my_posts: bool = Query(False, description="Return only current user's posts"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get social posts with filtering and pagination.
    
    - Returns active posts in descending order (newest first)
    - Supports filtering by tag, search, and user's own posts
    - Anonymous posts show limited user information
    """
    query = db.query(SocialPost).filter(SocialPost.is_active == True)
    
    if my_posts:
        query = query.filter(SocialPost.user_id == current_user.id)
    
    if tag_id:
        query = query.join(SocialPostTag).filter(SocialPostTag.tag_id == tag_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                SocialPost.title.ilike(search_term),
                SocialPost.content.ilike(search_term)
            )
        )
    
    posts = query.order_by(desc(SocialPost.created_at)).offset(skip).limit(limit).all()
    
    return posts

@router.get("/posts/{post_id}", response_model=SocialPostResponse)
async def get_social_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific social post by ID."""
    post = db.query(SocialPost).filter(
        and_(
            SocialPost.id == post_id,
            SocialPost.is_active == True
        )
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return post

@router.put("/posts/{post_id}", response_model=SocialPostResponse)
async def update_social_post(
    post_id: int,
    post_update: SocialPostUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a social post.
    
    - Only the post author can update their posts
    - Supports updating title, content, and tags
    """
    post = db.query(SocialPost).filter(
        and_(
            SocialPost.id == post_id,
            SocialPost.user_id == current_user.id,
            SocialPost.is_active == True
        )
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or you don't have permission to edit it"
        )
    
    # Update fields
    update_data = post_update.dict(exclude_unset=True, exclude={'tag_ids'})
    for field, value in update_data.items():
        setattr(post, field, value)
    
    post.updated_at = datetime.utcnow()
    
    # Update tags if provided
    if post_update.tag_ids is not None:
        # Remove existing tags
        db.query(SocialPostTag).filter(SocialPostTag.post_id == post_id).delete()
        
        # Add new tags
        for tag_id in post_update.tag_ids:
            tag = db.query(SocialTag).filter(SocialTag.id == tag_id).first()
            if tag:
                post_tag = SocialPostTag(post_id=post_id, tag_id=tag_id)
                db.add(post_tag)
    
    db.commit()
    db.refresh(post)
    
    return post

@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_social_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a social post (soft delete).
    
    - Only the post author can delete their posts
    - Sets is_active to False instead of hard delete
    """
    post = db.query(SocialPost).filter(
        and_(
            SocialPost.id == post_id,
            SocialPost.user_id == current_user.id,
            SocialPost.is_active == True
        )
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or you don't have permission to delete it"
        )
    
    post.is_active = False
    post.updated_at = datetime.utcnow()
    
    db.commit()

# Social Comment Endpoints

@router.post("/posts/{post_id}/comments", response_model=SocialCommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: int,
    comment: SocialCommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add a comment to a social post.
    
    - Comments can be replies to other comments (threading)
    - Supports anonymous commenting
    """
    # Verify post exists and is active
    post = db.query(SocialPost).filter(
        and_(
            SocialPost.id == post_id,
            SocialPost.is_active == True
        )
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Verify parent comment exists if provided
    if comment.parent_comment_id:
        parent_comment = db.query(SocialComment).filter(
            and_(
                SocialComment.id == comment.parent_comment_id,
                SocialComment.post_id == post_id,
                SocialComment.is_active == True
            )
        ).first()
        
        if not parent_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent comment not found"
            )
    
    db_comment = SocialComment(
        post_id=post_id,
        user_id=current_user.id,
        parent_comment_id=comment.parent_comment_id,
        content=comment.content,
        is_anonymous=comment.is_anonymous,
        is_active=True
    )
    
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    return db_comment

@router.get("/posts/{post_id}/comments", response_model=List[SocialCommentResponse])
async def get_post_comments(
    post_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get comments for a specific post.
    
    - Returns active comments in chronological order
    - Includes nested replies
    """
    # Verify post exists
    post = db.query(SocialPost).filter(
        and_(
            SocialPost.id == post_id,
            SocialPost.is_active == True
        )
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    comments = db.query(SocialComment).filter(
        and_(
            SocialComment.post_id == post_id,
            SocialComment.is_active == True
        )
    ).order_by(SocialComment.created_at).offset(skip).limit(limit).all()
    
    return comments

@router.put("/comments/{comment_id}", response_model=SocialCommentResponse)
async def update_comment(
    comment_id: int,
    comment_update: SocialCommentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a comment (only by the comment author)."""
    comment = db.query(SocialComment).filter(
        and_(
            SocialComment.id == comment_id,
            SocialComment.user_id == current_user.id,
            SocialComment.is_active == True
        )
    ).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you don't have permission to edit it"
        )
    
    update_data = comment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(comment, field, value)
    
    comment.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(comment)
    
    return comment

@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a comment (soft delete, only by the comment author)."""
    comment = db.query(SocialComment).filter(
        and_(
            SocialComment.id == comment_id,
            SocialComment.user_id == current_user.id,
            SocialComment.is_active == True
        )
    ).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you don't have permission to delete it"
        )
    
    comment.is_active = False
    comment.updated_at = datetime.utcnow()
    
    db.commit()

# Social Like Endpoints

@router.post("/posts/{post_id}/like", status_code=status.HTTP_201_CREATED)
async def like_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Like or unlike a post.
    
    - Toggles like status (like if not liked, unlike if already liked)
    - Returns the current like status
    """
    # Verify post exists
    post = db.query(SocialPost).filter(
        and_(
            SocialPost.id == post_id,
            SocialPost.is_active == True
        )
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Check if user already liked the post
    existing_like = db.query(SocialLike).filter(
        and_(
            SocialLike.post_id == post_id,
            SocialLike.user_id == current_user.id
        )
    ).first()
    
    if existing_like:
        # Unlike the post
        db.delete(existing_like)
        action = "unliked"
    else:
        # Like the post
        like = SocialLike(
            post_id=post_id,
            user_id=current_user.id
        )
        db.add(like)
        action = "liked"
    
    db.commit()
    
    # Get updated like count
    like_count = db.query(SocialLike).filter(SocialLike.post_id == post_id).count()
    
    return {
        "action": action,
        "like_count": like_count,
        "user_liked": action == "liked"
    }

@router.get("/posts/{post_id}/likes")
async def get_post_likes(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get like information for a post."""
    # Verify post exists
    post = db.query(SocialPost).filter(
        and_(
            SocialPost.id == post_id,
            SocialPost.is_active == True
        )
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    like_count = db.query(SocialLike).filter(SocialLike.post_id == post_id).count()
    
    user_liked = db.query(SocialLike).filter(
        and_(
            SocialLike.post_id == post_id,
            SocialLike.user_id == current_user.id
        )
    ).first() is not None
    
    return {
        "like_count": like_count,
        "user_liked": user_liked
    }

# Social Tag Endpoints

@router.get("/tags", response_model=List[SocialTagResponse])
async def get_social_tags(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None, description="Search tag names"),
    db: Session = Depends(get_db)
):
    """
    Get available social tags.
    
    - Used for categorizing posts
    - Supports search functionality
    """
    query = db.query(SocialTag)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(SocialTag.name.ilike(search_term))
    
    tags = query.order_by(SocialTag.name).offset(skip).limit(limit).all()
    
    return tags

@router.get("/tags/{tag_id}/posts", response_model=List[SocialPostResponse])
async def get_posts_by_tag(
    tag_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get posts associated with a specific tag."""
    # Verify tag exists
    tag = db.query(SocialTag).filter(SocialTag.id == tag_id).first()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    posts = db.query(SocialPost).join(SocialPostTag).filter(
        and_(
            SocialPostTag.tag_id == tag_id,
            SocialPost.is_active == True
        )
    ).order_by(desc(SocialPost.created_at)).offset(skip).limit(limit).all()
    
    return posts

# Social Feed Endpoint

@router.get("/feed", response_model=SocialFeedResponse)
async def get_social_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get personalized social feed.
    
    - Returns recent posts with engagement metrics
    - Includes like counts and comment counts
    - Optimized for feed display
    """
    # Get recent posts with engagement data
    posts_query = db.query(
        SocialPost,
        func.count(SocialLike.id).label('like_count'),
        func.count(SocialComment.id).label('comment_count')
    ).outerjoin(SocialLike).outerjoin(SocialComment).filter(
        SocialPost.is_active == True
    ).group_by(SocialPost.id).order_by(
        desc(SocialPost.created_at)
    ).offset(skip).limit(limit)
    
    posts_with_metrics = posts_query.all()
    
    # Get user's liked posts for this batch
    post_ids = [post.SocialPost.id for post in posts_with_metrics]
    user_likes = db.query(SocialLike.post_id).filter(
        and_(
            SocialLike.post_id.in_(post_ids),
            SocialLike.user_id == current_user.id
        )
    ).all()
    
    liked_post_ids = {like.post_id for like in user_likes}
    
    # Format response
    feed_posts = []
    for post_data in posts_with_metrics:
        post = post_data.SocialPost
        feed_post = {
            "post": post,
            "like_count": post_data.like_count,
            "comment_count": post_data.comment_count,
            "user_liked": post.id in liked_post_ids
        }
        feed_posts.append(feed_post)
    
    return {
        "posts": feed_posts,
        "total_count": len(feed_posts),
        "has_more": len(feed_posts) == limit
    }

