from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO

class LyricLine:
    def __init__(self, text: str, start_time: float, end_time: float, syllable_count: int = 0):
        self.text = text
        self.start_time = start_time
        self.end_time = end_time
        self.syllable_count = syllable_count

def format_timestamp_lrc(seconds: float) -> str:
    """Format timestamp for LRC format [mm:ss.xx]"""
    minutes = int(seconds // 60)
    seconds = seconds % 60
    return f"[{minutes:02d}:{seconds:05.2f}]"

def format_timestamp_srt(seconds: float) -> str:
    """Format timestamp for SRT format HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

def generate_lrc_export(
    lines: List[LyricLine], 
    metadata: Optional[Dict[str, Any]] = None,
    include_metadata: bool = True
) -> str:
    """Generate LRC format export"""
    lrc_content = []
    
    if include_metadata and metadata:
        # Add metadata tags
        if metadata.get('title'):
            lrc_content.append(f"[ti:{metadata['title']}]")
        if metadata.get('artist'):
            lrc_content.append(f"[ar:{metadata['artist']}]")
        if metadata.get('album'):
            lrc_content.append(f"[al:{metadata['album']}]")
        if metadata.get('bpm'):
            lrc_content.append(f"[bpm:{metadata['bpm']}]")
        if metadata.get('key'):
            lrc_content.append(f"[key:{metadata['key']}]")
        
        # Add generation info
        lrc_content.append(f"[tool:BeatLyrics AI]")
        lrc_content.append(f"[ve:1.0]")
        lrc_content.append("")
    
    # Add lyrics with timestamps
    for line in lines:
        timestamp = format_timestamp_lrc(line.start_time)
        lrc_content.append(f"{timestamp}{line.text}")
    
    return "\n".join(lrc_content)

def generate_srt_export(
    lines: List[LyricLine], 
    metadata: Optional[Dict[str, Any]] = None,
    include_metadata: bool = True
) -> str:
    """Generate SRT format export"""
    srt_content = []
    
    if include_metadata and metadata:
        # Add metadata as first subtitle
        metadata_lines = []
        if metadata.get('title'):
            metadata_lines.append(f"Title: {metadata['title']}")
        if metadata.get('bpm'):
            metadata_lines.append(f"BPM: {metadata['bpm']}")
        if metadata.get('key'):
            metadata_lines.append(f"Key: {metadata['key']}")
        
        if metadata_lines:
            srt_content.extend([
                "1",
                "00:00:00,000 --> 00:00:03,000",
                "\n".join(metadata_lines),
                ""
            ])
    
    # Add lyrics as subtitles
    start_index = 2 if (include_metadata and metadata) else 1
    
    for i, line in enumerate(lines, start=start_index):
        start_time = format_timestamp_srt(line.start_time)
        end_time = format_timestamp_srt(line.end_time)
        
        srt_content.extend([
            str(i),
            f"{start_time} --> {end_time}",
            line.text,
            ""
        ])
    
    return "\n".join(srt_content)

def generate_txt_export(
    lines: List[LyricLine], 
    metadata: Optional[Dict[str, Any]] = None,
    include_timestamps: bool = False,
    include_metadata: bool = True
) -> str:
    """Generate plain text format export"""
    txt_content = []
    
    if include_metadata and metadata:
        txt_content.append("=" * 50)
        txt_content.append("BEATLYRICS GENERATED LYRICS")
        txt_content.append("=" * 50)
        txt_content.append("")
        
        if metadata.get('title'):
            txt_content.append(f"Title: {metadata['title']}")
        if metadata.get('artist'):
            txt_content.append(f"Artist: {metadata['artist']}")
        if metadata.get('bpm'):
            txt_content.append(f"BPM: {metadata['bpm']}")
        if metadata.get('key'):
            txt_content.append(f"Key: {metadata['key']}")
        if metadata.get('duration'):
            txt_content.append(f"Duration: {metadata['duration']:.1f}s")
        
        txt_content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        txt_content.append("")
        txt_content.append("-" * 50)
        txt_content.append("")
    
    # Add lyrics
    for line in lines:
        if include_timestamps:
            timestamp = f"[{line.start_time:.1f}s] "
            txt_content.append(f"{timestamp}{line.text}")
        else:
            txt_content.append(line.text)
    
    if include_metadata and metadata:
        txt_content.append("")
        txt_content.append("-" * 50)
        txt_content.append("Generated with BeatLyrics AI")
        txt_content.append("https://beatlyrics.ai")
    
    return "\n".join(txt_content)

def generate_pdf_export(
    lines: List[LyricLine], 
    metadata: Optional[Dict[str, Any]] = None,
    include_timestamps: bool = False,
    include_metadata: bool = True,
    font_size: int = 12
) -> bytes:
    """Generate PDF format export"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=1*inch, bottomMargin=1*inch)
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12
    )
    
    lyric_style = ParagraphStyle(
        'CustomLyric',
        parent=styles['Normal'],
        fontSize=font_size,
        spaceAfter=8,
        leftIndent=20
    )
    
    timestamp_style = ParagraphStyle(
        'TimestampStyle',
        parent=styles['Normal'],
        fontSize=font_size-2,
        textColor='gray',
        spaceAfter=8,
        leftIndent=20
    )
    
    story = []
    
    # Add title and metadata
    if include_metadata and metadata:
        title = metadata.get('title', 'Generated Lyrics')
        story.append(Paragraph(title, title_style))
        
        if metadata.get('artist'):
            story.append(Paragraph(f"Artist: {metadata['artist']}", heading_style))
        
        # Metadata table
        metadata_info = []
        if metadata.get('bpm'):
            metadata_info.append(f"BPM: {metadata['bpm']}")
        if metadata.get('key'):
            metadata_info.append(f"Key: {metadata['key']}")
        if metadata.get('duration'):
            metadata_info.append(f"Duration: {metadata['duration']:.1f}s")
        
        if metadata_info:
            story.append(Paragraph(" | ".join(metadata_info), styles['Normal']))
        
        story.append(Spacer(1, 20))
        story.append(Paragraph("Lyrics", heading_style))
    
    # Add lyrics
    for line in lines:
        if include_timestamps:
            timestamp_text = f"[{line.start_time:.1f}s - {line.end_time:.1f}s]"
            story.append(Paragraph(timestamp_text, timestamp_style))
        
        story.append(Paragraph(line.text, lyric_style))
    
    # Add footer
    if include_metadata:
        story.append(Spacer(1, 30))
        story.append(Paragraph("Generated with BeatLyrics AI", styles['Normal']))
        story.append(Paragraph(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def get_export_filename(format_type: str, metadata: Optional[Dict[str, Any]] = None) -> str:
    """Generate appropriate filename for export"""
    base_name = "lyrics"
    
    if metadata and metadata.get('title'):
        # Clean title for filename
        title = metadata['title']
        # Remove invalid filename characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            title = title.replace(char, '')
        base_name = title.lower().replace(' ', '_')
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{base_name}_{timestamp}.{format_type}"
