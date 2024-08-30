
import re
from typing import Dict, NamedTuple, Optional
from api.auth.role_enum import RoleEnum

class PathInfo(NamedTuple):
    role: RoleEnum
    has_subroles:bool
    
    
class PathConfig:
    def __init__(self, routes):
        self.routes = routes

    def get_path_info(self, path, method):
        normalized_path = path.rstrip('/')  # Trailing slashes entfernen

        # Zuerst nach einer exakten Übereinstimmung suchen
        exact_match = self.routes.get(normalized_path, {}).get(method)
        if exact_match:
            return exact_match

        # Überprüfen von Mustern mit Variablen (spezifische Routen zuerst)
        for route in self.routes.keys():
            if method in self.routes[route]:
                if self._path_matches(route, normalized_path):
                    return self.routes[route][method]

        return None

    def _path_matches(self, route, path):
        route_parts = route.strip('/').split('/')
        path_parts = path.strip('/').split('/')

        if len(route_parts) != len(path_parts):
            return False

        for route_part, path_part in zip(route_parts, path_parts):
            if not (route_part.startswith('{') and route_part.endswith('}')) and route_part != path_part:
                return False

        return True
    
    def get_all_paths_and_methods(self) -> tuple:
        paths_and_methods = []

        for route, methods in self.routes.items():
            for method in methods:
                paths_and_methods.append((route, method))

        return tuple(paths_and_methods)
        
    

path_config = PathConfig({
    
    # fastapi
    '/openapi.json':{
        "GET": PathInfo(role=RoleEnum.EXTERNAL, has_subroles=True), 
        "HEAD": PathInfo(role=RoleEnum.EXTERNAL, has_subroles=True)
    },

    '/docs':{
        "GET": PathInfo(role=RoleEnum.EXTERNAL, has_subroles=True), 
        "HEAD": PathInfo(role=RoleEnum.EXTERNAL, has_subroles=True)
    },

    '/docs/oauth2-redirect':{
        "GET": PathInfo(role=RoleEnum.EXTERNAL, has_subroles=True), 
        "HEAD": PathInfo(role=RoleEnum.EXTERNAL, has_subroles=True)
    },

    '/redoc':{
        "GET": PathInfo(role=RoleEnum.EXTERNAL, has_subroles=True), 
        "HEAD": PathInfo(role=RoleEnum.EXTERNAL, has_subroles=True)
    },
    
    # root 
    '/':                                   {"GET": PathInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},

    # Static routes
    '/static/covers/{filename}':           {"GET": PathInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},
    '/static/demo_slot/{filename}':        {"GET": PathInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},
    '/static/edits/{filename}':            {"GET": PathInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},
    '/static/occupied_slots/{filename}':   {"GET": PathInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},
    '/static/songs/{filename}':            {"GET": PathInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},
    
    # testroutes
    '/testing/1':            {"GET": PathInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},
    '/testing/2':            {"GET": PathInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},
    '/testing/3':            {"GET": PathInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},
    '/testing/4':            {"POST": PathInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},
    
    # song
    '/song/':                            {"POST":   PathInfo(role=RoleEnum.ADMIN, has_subroles=True)},
    '/song/{song_id}':                   {
                                            "DELETE": PathInfo(role=RoleEnum.ADMIN, has_subroles=True),
                                            "GET":    PathInfo(role=RoleEnum.EXTERNAL, has_subroles=True)
                                         },
    '/song/list':                        {"GET":    PathInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},
    
    # group
    '/group':                           {"POST": PathInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},
    '/group/{group_id}':                  {
                                            "GET": PathInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=True),
                                            "DELETE": PathInfo(role=RoleEnum.GROUP_CREATOR, has_subroles=True)
                                          },
    '/group/{group_id}/role':             {"GET": PathInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},
    '/group/{group_id}/groupExists':      {"GET": PathInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},
    '/group/{group_id}/listMembers':      {"GET": PathInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=True)},    

    # user
    '/user/invite':                     {"POST": PathInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=True)},    
    '/user/acceptInvite':               {"POST": PathInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},    
    '/user/loginRequest':               {"POST": PathInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},    
    '/user/login':                      {"POST": PathInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},    
    
    # edit
    '/edit/{edit_id}/goLive':           {"POST": PathInfo(role=RoleEnum.GROUP_CREATOR, has_subroles=True)},    
    '/edit/{edit_id}':                  {"DELETE": PathInfo(role=RoleEnum.GROUP_CREATOR, has_subroles=True)},    
    '/edit/':                           {"POST": PathInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=True)},    
    '/edit/group/{group_id}/list':      {"GET": PathInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=True)},    
    '/edit/group/{group_id}/{edit_id}': {"GET": PathInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=True)},    
    '/edit/group/{group_id}/{edit_id}/slot/{occupied_slot_id}' : {
        "DELETE": PathInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=True),
        "POST": PathInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=True),
    },
    '/edit/group/{group_id}/{edit_id}/slot/{slot_id}' : {
        "PUT": PathInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=True),
    }

})