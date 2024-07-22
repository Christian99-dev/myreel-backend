from api.auth.role import RoleEnum
from api.config.path_roles import path_roles
from main import app
import logging
logger = logging.getLogger("testing")

def test_all_paths_have_role_configuration():

    routes = [route.path for route in app.router.routes]

    # Überprüfe, dass alle Routen in path_roles definiert sind
    missing_in_path_roles = [route for route in routes if route not in path_roles]
    assert not missing_in_path_roles, f"Fehlende Routen in path_roles: {missing_in_path_roles}"

    # # Überprüfe, dass jede Route in path_roles eine RoleEnum hat
    for route, role in path_roles.items():
        assert isinstance(role, RoleEnum), f"Die Rolle für den Pfad {route} ist keine gültige RoleEnum: {role}"
    
    # # Überprüfe, dass alle in path_roles definierten Routen in der OpenAPI-Spezifikation enthalten sind
    routes_in_path_roles = [route for route in path_roles.keys()]
    missing_in_openapi = [route for route in routes_in_path_roles if route not in routes]
    assert not missing_in_openapi, f"Routen in path_roles fehlen in der OpenAPI-Spezifikation: {missing_in_openapi}"

    # # Überprüfe, dass keine zusätzlichen Routen in der OpenAPI-Spezifikation vorhanden sind, die nicht in path_roles definiert sind
    additional_in_openapi = [route for route in routes if route not in path_roles]
    assert not additional_in_openapi, f"Zusätzliche Routen in der OpenAPI-Spezifikation: {additional_in_openapi}"