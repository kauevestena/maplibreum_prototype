# Error Handling and Robustness in MapLibreum

This document outlines the error handling improvements implemented in MapLibreum to address potential pitfalls and enhance the robustness of the library.

## Overview of Improvements

MapLibreum has been enhanced with comprehensive error handling and input validation to prevent common issues such as:

- Silent failures in network requests
- Invalid URL handling leading to security vulnerabilities
- Poor parameter validation causing runtime errors
- Lack of debugging information when things go wrong

## HTTP Request Handling

### Enhanced Scrapping Script (`misc/maplibre_examples/scrapping.py`)

The MapLibre examples scrapping script has been significantly improved with:

#### Robust HTTP Session Configuration
```python
def create_robust_session() -> requests.Session:
    """Create a requests session with retry strategy and proper configuration."""
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=BACKOFF_FACTOR,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False
    )
```

#### Features:
- **Automatic Retries**: Handles transient failures with exponential backoff
- **Timeout Protection**: 30-second timeout prevents hanging requests
- **Status Code Validation**: Proper handling of 404, 403, 429, and 5xx errors
- **Rate Limiting**: Configurable delays between requests
- **Comprehensive Logging**: Structured logging for debugging and monitoring

#### Error Handling Patterns:
```python
def safe_http_request(session: requests.Session, url: str, description: str = "") -> Optional[requests.Response]:
    """Make a safe HTTP request with proper error handling."""
    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            return response
        else:
            logger.warning(f"HTTP {response.status_code} for {url}")
            return None
    except requests.exceptions.Timeout:
        logger.error(f"Request timeout after {REQUEST_TIMEOUT}s: {url}")
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error: {url}")
    except Exception as e:
        logger.error(f"Unexpected error fetching {url}: {e}")
    
    return None
```

## URL Validation and Security

### Core Library Improvements (`maplibreum/core.py`)

The core MapLibreum library now includes comprehensive URL validation:

#### URL Validation Function
```python
def validate_url(url: str, allow_relative: bool = True) -> bool:
    """Validate URL format for security and correctness."""
    # Validates HTTP/HTTPS schemes only
    # Blocks javascript:, data:, and other potentially dangerous schemes
    # Supports both absolute and relative URLs as needed
```

#### Enhanced Methods:

**`add_external_script()`**:
- Validates script URLs to prevent XSS attacks
- Blocks `javascript:` and `data:` schemes
- Provides clear error messages for invalid URLs

**`add_tile_layer()`**:
- Validates tile server URLs (absolute URLs only)
- Validates tile size, zoom levels, and other parameters
- Comprehensive subdomain validation
- Detailed error messages for debugging

## Parameter Validation

### Input Validation Patterns

All public methods now include comprehensive parameter validation:

```python
# Example: Tile layer validation
if not isinstance(url, str) or not url.strip():
    raise ValueError("add_tile_layer requires a valid tile URL")

if not validate_url(url, allow_relative=False):
    raise ValueError(f"Invalid tile URL format: '{url}'. Tile URLs must be absolute (http/https).")

if not isinstance(tile_size, int) or tile_size <= 0:
    raise ValueError("tile_size must be a positive integer")
```

### Validation Features:
- **Type Checking**: Ensures parameters are of expected types
- **Range Validation**: Validates numeric parameters are within acceptable ranges
- **Format Validation**: Uses URL parsing to validate format correctness
- **Security Validation**: Prevents injection attacks through URL validation

## Logging and Debugging

### Structured Logging

The library now uses Python's standard logging module for better debugging:

```python
import logging

logger = logging.getLogger(__name__)

# Usage examples:
logger.info(f"Successfully processed {count} items")
logger.warning(f"Retrying failed request to {url}")
logger.error(f"Failed to validate URL: {url}")
logger.debug(f"Added external script: {src}")
```

### Benefits:
- **Configurable Log Levels**: Control verbosity in different environments
- **Structured Messages**: Consistent format for easier parsing
- **Context Information**: Include relevant details for debugging
- **Performance Impact**: Debug logging only active when needed

## Error Prevention Strategies

### 1. Input Validation
- Validate all external inputs at method boundaries
- Use type hints and runtime checking
- Provide clear error messages with suggestions

### 2. Defensive Programming
- Handle edge cases explicitly
- Use safe defaults where appropriate
- Validate data before processing

### 3. Resource Management
- Set timeouts for external requests
- Implement retry strategies with backoff
- Clean up resources properly

### 4. Security Considerations
- Validate URLs to prevent injection attacks
- Sanitize user inputs
- Use safe defaults for security-sensitive parameters

## Testing

### Comprehensive Test Coverage

The error handling improvements include extensive test coverage:

- **URL Validation Tests**: Test valid/invalid URL patterns
- **Parameter Validation Tests**: Test edge cases and error conditions
- **Network Error Simulation**: Test timeout and connection error handling
- **Security Tests**: Verify XSS and injection prevention

### Running Tests

```bash
# Run all error handling tests
pytest tests/test_error_handling_improvements.py -v

# Run scrapping improvement tests
pytest tests/test_scrapping_improvements.py -v

# Run full test suite
pytest tests/ -v
```

## Best Practices for Contributors

### When Adding New Features:

1. **Validate Inputs**: Always validate parameters at method entry points
2. **Handle Errors Gracefully**: Provide meaningful error messages
3. **Log Important Events**: Use appropriate log levels
4. **Test Error Conditions**: Include tests for failure scenarios
5. **Document Behavior**: Clearly document error conditions and exceptions

### Example Pattern:
```python
def new_method(self, url: str, timeout: int = 30) -> bool:
    """Example method with proper error handling."""
    
    # Input validation
    if not isinstance(url, str) or not url.strip():
        raise ValueError("URL is required and must be a non-empty string")
    
    if not validate_url(url):
        raise ValueError(f"Invalid URL format: {url}")
    
    if not isinstance(timeout, int) or timeout <= 0:
        raise ValueError("Timeout must be a positive integer")
    
    try:
        # Main logic here
        result = perform_operation(url, timeout)
        logger.info(f"Successfully processed {url}")
        return result
        
    except SpecificException as e:
        logger.error(f"Specific error processing {url}: {e}")
        raise ValueError(f"Failed to process URL: {e}") from e
        
    except Exception as e:
        logger.error(f"Unexpected error processing {url}: {e}")
        raise
```

## Migration Guide

### For Existing Code

Most existing code will continue to work unchanged. However, some previously accepted invalid inputs may now raise `ValueError`:

**Before (would silently fail or cause runtime errors):**
```python
m.add_external_script("")  # Empty string
m.add_tile_layer("javascript:alert('xss')")  # Security risk
m.add_tile_layer("https://example.com", tile_size=0)  # Invalid parameter
```

**After (raises clear ValueError):**
```python
# These now raise ValueError with descriptive messages
try:
    m.add_external_script("")
except ValueError as e:
    print(f"Error: {e}")  # "add_external_script requires a script URL"
```

### Benefits of Migration

- **Earlier Error Detection**: Problems caught at input validation rather than runtime
- **Better Security**: Prevention of XSS and injection attacks
- **Improved Debugging**: Clear error messages and logging
- **More Robust Applications**: Graceful handling of network issues

## Configuration Options

### Logging Configuration

```python
import logging

# Enable debug logging for development
logging.getLogger("maplibreum").setLevel(logging.DEBUG)

# Configure custom format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logging.getLogger("maplibreum").addHandler(handler)
```

### Network Configuration

For the scrapping script, you can customize network behavior:

```python
# In misc/maplibre_examples/scrapping.py
REQUEST_TIMEOUT = 60  # Increase timeout for slow networks
MAX_RETRIES = 5       # More retries for unstable connections
RATE_LIMIT_DELAY = 0.5  # Slower rate limiting
```

This comprehensive error handling framework makes MapLibreum more robust, secure, and maintainable while providing clear feedback when issues occur.