from django.core.exceptions import ValidationError

def file_size_validator(file, max_size_in_mb=5):
    """
    Validates that the file size does not exceed the specified limit.
    
    Args:
        file: The file to be validated.
        max_size_in_mb (int, optional): The maximum allowed file size in MB. Defaults to 5 MB.
    
    Raises:
        ValidationError: If the file size exceeds the specified limit.
    """
    max_size_in_bytes = max_size_in_mb * 1024 * 1024
    if file.size > max_size_in_bytes:
        raise ValidationError(f'File size cannot exceed {max_size_in_mb}MB. Please upload a smaller file.')
