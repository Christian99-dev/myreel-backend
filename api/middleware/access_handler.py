import logging
import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from api.config.endpoints import EndpointConfig
from api.security.role_class import Role, RoleInfos
from api.utils.jwt import jwt
from api.utils.routes.extract_role_credentials_from_request import \
    extract_role_credentials_from_request

logger = logging.getLogger("middleware.access_handler")


class AccessHandlerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, path_config: EndpointConfig, get_database_session):
        super().__init__(app)
        self.path_config = path_config
        self.get_database_session = get_database_session

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()  # Track request start time

        # Extract the path and method for logging
        path = request.url.path
        method = request.method

        # Log the basic request information (first line)
        logger.info(f"Request Info: Path={path}, Method={method}")
        
        # Retrieve path info from the config
        pathInfo = self.path_config.get_path_info(path, method)

        if pathInfo is None:
            status_code = 401
            duration = time.time() - start_time
            # Log the result information (second line)
            logger.info(f"Access Result: Status={status_code}, Duration={duration:.4f}s, Role=None, Required Role=None, Path={path}")
            return Response(status_code=status_code)

        # Extract credentials
        credentials = await extract_role_credentials_from_request(request)

        admintoken = credentials.admintoken
        groupid = credentials.groupid
        editid = credentials.editid

        # Extract user ID from JWT
        userid = None
        jwt_error = None
        try:
            userid = jwt.read_jwt(credentials.jwt)
        except Exception as e:
            jwt_error = str(e)
            userid = None

        # Use the database session
        database_session_generator = self.get_database_session()
        database_session = next(database_session_generator)

        # Initialize role with the extracted credentials
        role = Role(role_infos=RoleInfos(admintoken=admintoken, userid=userid, groupid=groupid, editid=editid), database_session=database_session)
        
        # Check if the role has access
        if not role.hasAccess(pathInfo):
            status_code = 403
            duration = time.time() - start_time
            # Log the result information (combined line)
            logger.info(f"Access Result: Status={status_code}, Duration={duration:.4f}s, Role={role._role.name}, Required Role={pathInfo.role.name}, Path={path}, JWT Error={jwt_error}")
            return Response(status_code=status_code)

        # Proceed if access is granted
        response = await call_next(request)
        
        # Log the result of the request (combined line)
        duration = time.time() - start_time
        logger.info(f"Access Result: Status={response.status_code}, Duration={duration:.4f}s, Role={role._role.name}, Required Role={pathInfo.role.name}, Path={path}, JWT Error={jwt_error}")

        return response
