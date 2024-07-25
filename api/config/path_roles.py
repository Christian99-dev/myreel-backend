from typing import Dict, NamedTuple
from api.auth.role_enum import RoleEnum

class PathInfo(NamedTuple):
    role: RoleEnum
    has_subroles: bool
    
#TODO SONG
path_roles: Dict[str, PathInfo] = {
    # fastapi 
    '/openapi.json':            PathInfo(role=RoleEnum.EXTERNAL,    has_subroles=False),
    '/docs':                    PathInfo(role=RoleEnum.EXTERNAL,    has_subroles=False),
    '/docs/oauth2-redirect':    PathInfo(role=RoleEnum.EXTERNAL,    has_subroles=False), 
    '/redoc':                   PathInfo(role=RoleEnum.EXTERNAL,    has_subroles=False),
    
    # root
    '/':                        PathInfo(role=RoleEnum.EXTERNAL,    has_subroles=False),
            
    # songs
    # '/song/create':             PathInfo(role=RoleEnum.ADMIN,     has_subroles=True), 
    # '/song/delete':             PathInfo(role=RoleEnum.ADMIN,     has_subroles=True), 
    # '/song/update':             PathInfo(role=RoleEnum.ADMIN,     has_subroles=True), 
    # '/song/get/{song_id}':      PathInfo(role=RoleEnum.ADMIN,     has_subroles=True),
    # '/song/list':               PathInfo(role=RoleEnum.ADMIN,     has_subroles=True), 
    
    # group
    # '/group/delete':            PathInfo(role=RoleEnum.ADMIN,      has_subroles=True), 
    # '/group/get':               PathInfo(role=RoleEnum.ADMIN,      has_subroles=True), 
}

