from api.auth.roleEnum import RoleEnum
from api.config.path_roles import PathInfo, path_roles
from main import app

def test_all_paths_have_role_configuration():
    routes = [route.path for route in app.router.routes]

    # Überprüfe, dass alle Routen in path_roles definiert sind
    missing_in_path_roles = [route for route in routes if route not in path_roles]
    assert not missing_in_path_roles, f"Fehlende Routen in path_roles: {missing_in_path_roles}"

    # Überprüfe, dass jede Route in path_roles eine PathInfo-Instanz mit einer RoleEnum hat
    for route, path_info in path_roles.items():
        assert isinstance(path_info, PathInfo), f"Die Konfiguration für den Pfad {route} ist keine gültige PathInfo-Instanz: {path_info}"
        assert isinstance(path_info.role, RoleEnum), f"Die Rolle für den Pfad {route} ist keine gültige RoleEnum: {path_info.role}"
        assert isinstance(path_info.has_subroles, bool), f"Der has_subroles-Wert für den Pfad {route} ist kein gültiger Boolean: {path_info.has_subroles}"
    
    # Überprüfe, dass alle in path_roles definierten Routen in der FastAPI-Spezifikation enthalten sind
    routes_in_path_roles = list(path_roles.keys())
    missing_in_openapi = [route for route in routes_in_path_roles if route not in routes]
    assert not missing_in_openapi, f"Routen in path_roles fehlen in der FastAPI-Spezifikation: {missing_in_openapi}"

    # Überprüfe, dass keine zusätzlichen Routen in der FastAPI-Spezifikation vorhanden sind, die nicht in path_roles definiert sind
    additional_in_openapi = [route for route in routes if route not in path_roles]
    assert not additional_in_openapi, f"Zusätzliche Routen in der FastAPI-Spezifikation: {additional_in_openapi}"