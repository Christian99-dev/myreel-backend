from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError

from api.exceptions.file_validation.file_validation import (
    FileTooLargeException, InvalidFileFormatException,
    InvalidFileTypeException)
from api.exceptions.media_manipulation.media_manipulation import \
    MediaManipulationError
from api.exceptions.sessions.email import (EmailConfigurationError,
                                           EmailConnectionError,
                                           EmailDeliveryError, EmailSendError)
from api.exceptions.sessions.files import (DirectoryNotFoundError,
                                           FileDeleteError,
                                           FileExistsInSessionError,
                                           FileNotFoundInSessionError,
                                           FileSessionError, FileUpdateError)
from api.exceptions.sessions.instagram import (FTPConnectionError,
                                               FTPUploadError,
                                               InstagramUploadError,
                                               MediaContainerCreationError,
                                               VideoPublishError)
from main import app

""" FILE VALIDATION """

@app.exception_handler(InvalidFileTypeException)
async def invalid_file_type_exception_handler(request: Request, exc: InvalidFileTypeException):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.exception_handler(InvalidFileFormatException)
async def invalid_file_format_exception_handler(request: Request, exc: InvalidFileFormatException):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.exception_handler(FileTooLargeException)
async def file_too_large_exception_handler(request: Request, exc: FileTooLargeException):
    return JSONResponse(
        status_code=413,  # Payload Too Large
        content={"detail": str(exc)}
    )


""" MEDIA MANIPULATION """

@app.exception_handler(MediaManipulationError)
async def media_manipulation_error_handler(request: Request, exc: MediaManipulationError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


""" EMAIL SESSION """

@app.exception_handler(EmailSendError)
async def email_send_error_handler(request: Request, exc: EmailSendError):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

@app.exception_handler(EmailConfigurationError)
async def email_configuration_error_handler(request: Request, exc: EmailConfigurationError):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

@app.exception_handler(EmailConnectionError)
async def email_connection_error_handler(request: Request, exc: EmailConnectionError):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

@app.exception_handler(EmailDeliveryError)
async def email_delivery_error_handler(request: Request, exc: EmailDeliveryError):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )


""" FILE SESSION """

@app.exception_handler(FileSessionError)
async def file_session_error_handler(request: Request, exc: FileSessionError):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

@app.exception_handler(FileNotFoundInSessionError)
async def file_not_found_in_session_error_handler(request: Request, exc: FileNotFoundInSessionError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
    )

@app.exception_handler(FileExistsInSessionError)
async def file_exists_in_session_error_handler(request: Request, exc: FileExistsInSessionError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.exception_handler(DirectoryNotFoundError)
async def directory_not_found_error_handler(request: Request, exc: DirectoryNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
    )

@app.exception_handler(FileUpdateError)
async def file_update_error_handler(request: Request, exc: FileUpdateError):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

@app.exception_handler(FileDeleteError)
async def file_delete_error_handler(request: Request, exc: FileDeleteError):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )


""" INSTAGRAM """

@app.exception_handler(InstagramUploadError)
async def instagram_upload_error_handler(request: Request, exc: InstagramUploadError):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

@app.exception_handler(FTPConnectionError)
async def ftp_connection_error_handler(request: Request, exc: FTPConnectionError):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

@app.exception_handler(FTPUploadError)
async def ftp_upload_error_handler(request: Request, exc: FTPUploadError):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

@app.exception_handler(MediaContainerCreationError)
async def media_container_creation_error_handler(request: Request, exc: MediaContainerCreationError):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

@app.exception_handler(VideoPublishError)
async def video_publish_error_handler(request: Request, exc: VideoPublishError):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )


""" SQLALCHEMY """

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.exception_handler(NoResultFound)
async def no_result_found_error_handler(request: Request, exc: NoResultFound):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)}
    )
