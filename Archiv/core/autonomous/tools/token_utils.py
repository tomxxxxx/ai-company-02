"""
Token utility functions for managing API rate limits and token-efficient operations.
"""

def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in a text string.
    Uses a simple heuristic: approximately 4 characters = 1 token.
    
    Args:
        text: The text to analyze
        
    Returns:
        Estimated number of tokens
    """
    if not text:
        return 0
    
    # Simple heuristic: ~4 characters per token
    return len(text) // 4

def is_text_too_large(text: str, max_tokens: int = 1000) -> bool:
    """
    Check if text would exceed token limits.
    
    Args:
        text: The text to check
        max_tokens: Maximum allowed tokens (default: 1000)
        
    Returns:
        True if text is too large, False otherwise
    """
    estimated = estimate_tokens(text)
    return estimated > max_tokens

def calculate_chunk_size(total_lines: int, max_tokens_per_chunk: int = 1000) -> int:
    """
    Calculate optimal chunk size in lines for a file.
    Assumes ~20 tokens per line on average.
    
    Args:
        total_lines: Total number of lines in the file
        max_tokens_per_chunk: Maximum tokens per chunk
        
    Returns:
        Number of lines per chunk
    """
    # Assume ~20 tokens per line on average
    tokens_per_line = 20
    lines_per_chunk = max_tokens_per_chunk // tokens_per_line
    
    # Minimum 10 lines, maximum 100 lines per chunk
    return max(10, min(100, lines_per_chunk))

def get_chunk_ranges(total_lines: int, chunk_size: int = 50) -> list:
    """
    Generate start_line and end_line ranges for chunking a file.
    
    Args:
        total_lines: Total number of lines in the file
        chunk_size: Lines per chunk
        
    Returns:
        List of (start_line, end_line) tuples
    """
    chunks = []
    for start in range(1, total_lines + 1, chunk_size):
        end = min(start + chunk_size - 1, total_lines)
        chunks.append((start, end))
    return chunks