"""
Configuration validation utilities for VoidWalker v4.
Ensures all configuration values are within acceptable ranges and formats.
"""
import os
import re
from typing import Optional, List
from common.constants import MIN_WORKERS, MAX_WORKERS, ABSOLUTE_MAX_DEPTH


class ConfigValidator:
    """Validates configuration parameters before use."""
    
    @staticmethod
    def validate_workers(count: int, disk_type: str = "auto") -> int:
        """
        Validate and normalize worker count.
        
        Args:
            count: Requested worker count
            disk_type: Disk type for context-aware suggestions
            
        Returns:
            Validated worker count (capped to safe range)
            
        Raises:
            ValueError: If count is negative or zero
        """
        if count < 1:
            raise ValueError(f"Worker count must be >= 1, got {count}")
        
        if count > MAX_WORKERS:
            import warnings
            warnings.warn(
                f"Worker count {count} exceeds recommended maximum {MAX_WORKERS}, "
                f"capping to {MAX_WORKERS} to prevent resource exhaustion"
            )
            return MAX_WORKERS
        
        return count
    
    @staticmethod
    def validate_depth_range(min_depth: int, max_depth: int) -> tuple[int, int]:
        """
        Validate min/max depth configuration.
        
        Args:
            min_depth: Minimum traversal depth
            max_depth: Maximum traversal depth
            
        Returns:
            Tuple of (validated_min, validated_max)
            
        Raises:
            ValueError: If depths are invalid or inverted
        """
        if min_depth < 0:
            raise ValueError(f"Minimum depth cannot be negative, got {min_depth}")
        
        if max_depth < min_depth:
            raise ValueError(
                f"Maximum depth ({max_depth}) cannot be less than minimum depth ({min_depth})"
            )
        
        if max_depth > ABSOLUTE_MAX_DEPTH:
            import warnings
            warnings.warn(
                f"Maximum depth {max_depth} exceeds safety limit {ABSOLUTE_MAX_DEPTH}, "
                f"capping to {ABSOLUTE_MAX_DEPTH}"
            )
            max_depth = ABSOLUTE_MAX_DEPTH
        
        return min_depth, max_depth
    
    @staticmethod
    def validate_path(path: str, must_exist: bool = True) -> str:
        """
        Validate and normalize filesystem path.
        
        Args:
            path: Path string to validate
            must_exist: If True, path must exist on filesystem
            
        Returns:
            Normalized absolute path
            
        Raises:
            ValueError: If path is invalid, empty, or doesn't exist (when required)
        """
        if not path or not path.strip():
            raise ValueError("Path cannot be empty or whitespace")
        
        # Normalize path
        path = path.strip()
        
        # Handle Windows drive letters without trailing slash (F: -> F:\\)
        if len(path) == 2 and path[1] == ':':
            path = path + '\\\\'
        
        # Convert to absolute path
        try:
            abs_path = os.path.abspath(path)
        except Exception as e:
            raise ValueError(f"Invalid path format '{path}': {e}")
        
        if must_exist:
            if not os.path.exists(abs_path):
                raise ValueError(f"Path does not exist: {abs_path}")
            
            if not os.path.isdir(abs_path):
                raise ValueError(f"Path is not a directory: {abs_path}")
            
            # Test read permissions
            try:
                os.listdir(abs_path)
            except PermissionError:
                raise ValueError(f"No permission to access: {abs_path}")
            except OSError as e:
                raise ValueError(f"Cannot access path: {abs_path} ({e})")
        
        return abs_path
    
    @staticmethod
    def validate_pattern(pattern: str, pattern_type: str = "name") -> str:
        """
        Validate wildcard patterns for filtering.
        
        Args:
            pattern: Pattern string (e.g., "*.tmp*", "node_modules")
            pattern_type: Type of pattern ("name" or "path")
            
        Returns:
            Validated pattern string
            
        Raises:
            ValueError: If pattern contains invalid characters
        """
        if not pattern or not pattern.strip():
            raise ValueError(f"{pattern_type.capitalize()} pattern cannot be empty")
        
        pattern = pattern.strip()
        
        # Check for unsafe characters (null bytes, control characters)
        if '\x00' in pattern:
            raise ValueError(f"Pattern cannot contain null bytes: {pattern}")
        
        # Validate wildcards are properly used
        if pattern_type == "path" and '**' in pattern:
            # Ensure ** is used correctly (not in middle of word)
            if re.search(r'\w\*\*|\*\*\w', pattern):
                import warnings
                warnings.warn(
                    f"Pattern '{pattern}' has ** in unexpected position, "
                    f"may not match as intended"
                )
        
        return pattern
    
    @staticmethod
    def validate_exclude_lists(
        exclude_paths: Optional[List[str]] = None,
        exclude_names: Optional[List[str]] = None
    ) -> tuple[List[str], List[str]]:
        """
        Validate lists of exclusion patterns.
        
        Args:
            exclude_paths: List of path patterns to exclude
            exclude_names: List of name patterns to exclude
            
        Returns:
            Tuple of (validated_paths, validated_names)
        """
        validated_paths = []
        if exclude_paths:
            for pattern in exclude_paths:
                try:
                    validated_paths.append(
                        ConfigValidator.validate_pattern(pattern, "path")
                    )
                except ValueError as e:
                    import warnings
                    warnings.warn(f"Skipping invalid path pattern: {e}")
        
        validated_names = []
        if exclude_names:
            for pattern in exclude_names:
                try:
                    validated_names.append(
                        ConfigValidator.validate_pattern(pattern, "name")
                    )
                except ValueError as e:
                    import warnings
                    warnings.warn(f"Skipping invalid name pattern: {e}")
        
        return validated_paths, validated_names
