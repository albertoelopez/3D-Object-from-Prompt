from fastapi import HTTPException
from typing import Optional


class AppException(Exception):
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class JobNotFoundException(AppException):
    def __init__(self, job_id: str):
        super().__init__(
            message=f"Job {job_id} not found",
            code="JOB_NOT_FOUND"
        )


class JobNotCompletedException(AppException):
    def __init__(self, job_id: str, status: str):
        super().__init__(
            message=f"Job {job_id} is not completed (status: {status})",
            code="JOB_NOT_COMPLETED"
        )


class FileNotFoundException(AppException):
    def __init__(self, filename: str):
        super().__init__(
            message=f"File {filename} not found",
            code="FILE_NOT_FOUND"
        )


class InvalidFileTypeException(AppException):
    def __init__(self, file_type: str, allowed_types: list):
        super().__init__(
            message=f"Invalid file type: {file_type}. Allowed types: {', '.join(allowed_types)}",
            code="INVALID_FILE_TYPE"
        )


class FileTooLargeException(AppException):
    def __init__(self, size: int, max_size: int):
        super().__init__(
            message=f"File too large: {size} bytes. Maximum allowed: {max_size} bytes",
            code="FILE_TOO_LARGE"
        )


class LLMServiceException(AppException):
    def __init__(self, provider: str, message: str):
        super().__init__(
            message=f"LLM service error ({provider}): {message}",
            code="LLM_SERVICE_ERROR"
        )


class GPUException(AppException):
    def __init__(self, message: str):
        super().__init__(
            message=f"GPU error: {message}",
            code="GPU_ERROR"
        )


def http_exception_from_app_exception(e: AppException, status_code: int = 400) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={"code": e.code, "message": e.message}
    )
