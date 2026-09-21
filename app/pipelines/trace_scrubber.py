import re
from typing import List, Tuple

class TraceScrubber:
    """
    Scrubs high-cardinality noise, timestamps, and customer PII from raw error traces.
    Normalizing logs and traces in this way drastically improves the quality of 
    vector embeddings by grouping similar semantic errors regardless of specific 
    identifiers.
    """
    def __init__(self):
        # Ordered list of (compiled regex, replacement token)
        # Order matters! Match more specific patterns before broader ones.
        self.scrub_rules: List[Tuple[re.Pattern, str]] = [
            # Email addresses (PII)
            (re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'), '<EMAIL>'),
            
            # IPv4 Addresses (PII / infrastructure noise)
            (re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'), '<IP_ADDRESS>'),
            
            # ISO-8601 Timestamps and variations (e.g., 2023-10-24T12:00:00Z)
            (re.compile(r'\b\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?\b'), '<TIMESTAMP>'),
            
            # Common Syslog/Web Log Timestamps (e.g., Oct 24 12:00:00)
            (re.compile(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\b'), '<TIMESTAMP>'),
            
            # UUIDs (High cardinality noise)
            (re.compile(r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b'), '<UUID>'),
            
            # Hexadecimal strings (e.g., Git hashes, memory addresses, object IDs - min length 8)
            (re.compile(r'\b0x[0-9a-fA-F]+\b|\b[0-9a-fA-F]{8,}\b'), '<HEX_ID>'),
            
            # Long numeric strings (often customer IDs, account IDs, or transaction IDs)
            (re.compile(r'\b\d{10,}\b'), '<NUMERIC_ID>'),
        ]

    def scrub(self, text: str) -> str:
        """
        Applies all regex replacement rules to scrub the input trace.
        """
        if not text:
            return text
            
        scrubbed_text = text
        for pattern, replacement in self.scrub_rules:
            scrubbed_text = pattern.sub(replacement, scrubbed_text)
            
        return scrubbed_text
