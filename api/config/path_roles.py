from typing import Dict
from api.auth.role import RoleEnum
    
path_roles: Dict[str, RoleEnum] = {
    # fastapi 
    '/openapi.json':            RoleEnum.EXTERNAL,
    '/docs':                    RoleEnum.EXTERNAL,
    '/docs/oauth2-redirect':    RoleEnum.EXTERNAL, 
    '/redoc':                   RoleEnum.EXTERNAL,
    
    # root
    '/':                        RoleEnum.EXTERNAL,        
    # songs
    '/song/create':             RoleEnum.ADMIN, 
    '/song/delete':             RoleEnum.ADMIN, 
    '/song/update':             RoleEnum.ADMIN, 
    '/song/get':                RoleEnum.ADMIN,
    '/song/list':               RoleEnum.ADMIN, 
    
    # group
    '/group/delete':            RoleEnum.ADMIN, 
    '/group/get':               RoleEnum.ADMIN, 
}

