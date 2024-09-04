from typing import NamedTuple
from api.security.role_enum import RoleEnum


class EndpointInfo(NamedTuple):
    role: RoleEnum
    has_subroles:bool
    
    
class EndpointConfig:
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
        
    