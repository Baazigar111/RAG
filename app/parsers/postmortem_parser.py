import re
from typing import Dict, List, Any
from pydantic import BaseModel

class PostMortemSegment(BaseModel):
    """Represents a semantically segmented chunk of a post-mortem document."""
    heading: str
    content: str
    metadata: Dict[str, Any] = {}

class PostMortemParser:
    """
    Parses and segments historical markdown post-mortems based on semantic 
    headings (e.g., Root Cause, Timeline, Remediation) rather than fixed 
    token lengths.
    """
    def __init__(self, target_headings: List[str] = None):
        # We can optionally use target_headings to filter or prioritize certain sections
        self.target_headings = target_headings or [
            "Root Cause", 
            "Timeline", 
            "Remediation", 
            "Summary", 
            "Impact", 
            "Action Items"
        ]

    def parse(self, markdown_text: str) -> List[PostMortemSegment]:
        """
        Segments the markdown text by headings.
        Content under each heading is collected until the next heading.
        """
        # Matches one or more '#' at the start of a line, followed by space, then the heading text.
        pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        
        segments = []
        matches = list(pattern.finditer(markdown_text))
        
        if not matches:
            # No headings found, treat the entire text as a single un-segmented document
            return [PostMortemSegment(heading="Document", content=markdown_text.strip())]
            
        # Extract any preamble (text before the first heading)
        first_match_start = matches[0].start()
        preamble = markdown_text[:first_match_start].strip()
        if preamble:
            segments.append(PostMortemSegment(heading="Preamble", content=preamble))
            
        for i, match in enumerate(matches):
            level = len(match.group(1))
            heading_text = match.group(2).strip()
            
            # Content starts right after the current heading ends
            content_start = match.end()
            
            # Content ends where the next heading begins, or at the end of the text
            if i + 1 < len(matches):
                content_end = matches[i+1].start()
            else:
                content_end = len(markdown_text)
                
            content = markdown_text[content_start:content_end].strip()
            
            if content:
                segments.append(PostMortemSegment(
                    heading=heading_text, 
                    content=content,
                    metadata={"level": level, "is_target": any(t.lower() in heading_text.lower() for t in self.target_headings)}
                ))
                
        return segments
