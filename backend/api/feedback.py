from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from typing import List

from models.feedback import Feedback, FeedbackRequest
from models.generation import Generation
from database import get_db
from utils.auth import get_current_user

router = APIRouter(prefix="/api/v1", tags=["feedback"])

@router.post("/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    http_request: Request,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit feedback for a generation"""
    
    # Verify generation exists
    generation = db.query(Generation).filter(Generation.id == request.generation_id).first()
    if not generation:
        raise HTTPException(status_code=404, detail="Generation not found")
    
    # Validate rating if provided
    if request.rating is not None and (request.rating < 1 or request.rating > 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    # Create feedback record
    feedback = Feedback(
        user_id=current_user.id if current_user else None,
        generation_id=request.generation_id,
        type=request.type,
        rating=request.rating,
        comment=request.comment,
        edits=request.edits,
        user_agent=http_request.headers.get("user-agent"),
        ip_address=http_request.client.host
    )
    
    db.add(feedback)
    db.commit()
    
    return {"message": "Feedback submitted successfully", "feedback_id": feedback.id}

@router.get("/generation/{generation_id}/feedback")
async def get_generation_feedback(
    generation_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get feedback for a generation (admin only)"""
    
    if not current_user or current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    feedback_list = db.query(Feedback)\
        .filter(Feedback.generation_id == generation_id)\
        .all()
    
    return [
        {
            "id": fb.id,
            "type": fb.type,
            "rating": fb.rating,
            "comment": fb.comment,
            "edits": fb.edits,
            "created_at": fb.created_at,
            "user_id": fb.user_id
        }
        for fb in feedback_list
    ]

@router.get("/feedback/stats")
async def get_feedback_stats(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get feedback statistics (admin only)"""
    
    if not current_user or current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Calculate basic stats
    total_feedback = db.query(Feedback).count()
    avg_rating = db.query(Feedback.rating).filter(Feedback.rating.isnot(None)).all()
    
    if avg_rating:
        avg_rating_value = sum(r[0] for r in avg_rating) / len(avg_rating)
    else:
        avg_rating_value = 0
    
    return {
        "total_feedback": total_feedback,
        "average_rating": round(avg_rating_value, 2),
        "rating_distribution": {
            "5_star": db.query(Feedback).filter(Feedback.rating == 5).count(),
            "4_star": db.query(Feedback).filter(Feedback.rating == 4).count(),
            "3_star": db.query(Feedback).filter(Feedback.rating == 3).count(),
            "2_star": db.query(Feedback).filter(Feedback.rating == 2).count(),
            "1_star": db.query(Feedback).filter(Feedback.rating == 1).count(),
        }
    }
