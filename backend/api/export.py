from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import io
from typing import Literal, Optional, Dict, Any

from ..models.generation import Generation
from ..database import get_db
from ..auth.jwt_handler import get_current_user
from ..utils.export_generators import (
    generate_lrc_export, 
    generate_srt_export, 
    generate_txt_export, 
    generate_pdf_export,
    get_export_filename,
    LyricLine
)

router = APIRouter(prefix="/export", tags=["export"])

class ExportRequest(BaseModel):
    generation_id: str
    format: Literal["lrc", "srt", "txt", "pdf"]
    include_timestamps: bool = True
    include_metadata: bool = True
    font_size: int = 12

def convert_lyrics_to_lines(lyrics_json: Dict[str, Any]) -> list[LyricLine]:
    """Convert lyrics JSON to LyricLine objects"""
    lines = []
    for line_data in lyrics_json.get("lines", []):
        lines.append(LyricLine(
            text=line_data.get("text", ""),
            start_time=line_data.get("start_time", 0.0),
            end_time=line_data.get("end_time", 0.0),
            syllable_count=line_data.get("syllable_count", 0)
        ))
    return lines

@router.post("/generate")
async def export_generation(
    request: ExportRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export generation in specified format"""
    
    # Get generation
    generation = db.query(Generation).filter(Generation.id == request.generation_id).first()
    if not generation:
        raise HTTPException(status_code=404, detail="Generation not found")
    
    if not generation.lyrics_json:
        raise HTTPException(status_code=400, detail="No lyrics available for export")
    
    # Get audio job for timing information
    job = generation.job
    if not job or not job.features:
        raise HTTPException(status_code=400, detail="Audio features not available")
    
    try:
        # Convert lyrics to LyricLine objects
        lines = convert_lyrics_to_lines(generation.lyrics_json)
        
        # Prepare metadata
        metadata = {
            "title": generation.title or "Generated Lyrics",
            "bpm": job.features.get("bpm"),
            "key": job.features.get("key"),
            "duration": job.features.get("duration"),
            "artist": generation.lyrics_json.get("metadata", {}).get("artist"),
            "album": generation.lyrics_json.get("metadata", {}).get("album")
        }
        
        if request.format == "lrc":
            content = generate_lrc_export(lines, metadata, request.include_metadata)
            media_type = "text/plain"
            filename = get_export_filename("lrc", metadata)
            
        elif request.format == "srt":
            content = generate_srt_export(lines, metadata, request.include_metadata)
            media_type = "text/plain"
            filename = get_export_filename("srt", metadata)
            
        elif request.format == "txt":
            content = generate_txt_export(
                lines, 
                metadata, 
                request.include_timestamps, 
                request.include_metadata
            )
            media_type = "text/plain"
            filename = get_export_filename("txt", metadata)
            
        elif request.format == "pdf":
            content = generate_pdf_export(
                lines, 
                metadata, 
                request.include_timestamps, 
                request.include_metadata,
                request.font_size
            )
            media_type = "application/pdf"
            filename = get_export_filename("pdf", metadata)
            
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
        
        # Convert string content to bytes if needed
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        # Return file as streaming response
        return StreamingResponse(
            io.BytesIO(content),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.get("/preview/{generation_id}")
async def preview_export(
    generation_id: str,
    format: Literal["lrc", "srt", "txt"],
    include_timestamps: bool = True,
    include_metadata: bool = True,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Preview export content without downloading"""
    
    generation = db.query(Generation).filter(Generation.id == generation_id).first()
    if not generation:
        raise HTTPException(status_code=404, detail="Generation not found")
    
    if not generation.lyrics_json:
        raise HTTPException(status_code=400, detail="No lyrics available")
    
    job = generation.job
    if not job or not job.features:
        raise HTTPException(status_code=400, detail="Audio features not available")
    
    try:
        # Convert lyrics to LyricLine objects
        lines = convert_lyrics_to_lines(generation.lyrics_json)
        
        # Prepare metadata
        metadata = {
            "title": generation.title or "Generated Lyrics",
            "bpm": job.features.get("bpm"),
            "key": job.features.get("key"),
            "duration": job.features.get("duration"),
            "artist": generation.lyrics_json.get("metadata", {}).get("artist"),
            "album": generation.lyrics_json.get("metadata", {}).get("album")
        }
        
        if format == "lrc":
            content = generate_lrc_export(lines, metadata, include_metadata)
        elif format == "srt":
            content = generate_srt_export(lines, metadata, include_metadata)
        elif format == "txt":
            content = generate_txt_export(lines, metadata, include_timestamps, include_metadata)
        else:
            raise HTTPException(status_code=400, detail="PDF preview not supported")
        
        return {"content": content}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")

@router.get("/formats")
async def get_export_formats():
    """Get available export formats and their descriptions"""
    return {
        "formats": [
            {
                "value": "lrc",
                "label": "LRC (Lyrics with timestamps)",
                "description": "Standard karaoke format with precise timestamps",
                "supports_timestamps": True,
                "supports_metadata": True
            },
            {
                "value": "srt",
                "label": "SRT (SubRip subtitle format)",
                "description": "Subtitle format compatible with video players",
                "supports_timestamps": True,
                "supports_metadata": True
            },
            {
                "value": "txt",
                "label": "TXT (Plain text)",
                "description": "Simple text format with optional timestamps",
                "supports_timestamps": True,
                "supports_metadata": True
            },
            {
                "value": "pdf",
                "label": "PDF (Formatted document)",
                "description": "Professional formatted document",
                "supports_timestamps": True,
                "supports_metadata": True,
                "supports_font_size": True
            }
        ]
    }
