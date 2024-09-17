
from starlette.routing import Mount, Route

from api.config.endpoints import EndpointConfig, EndpointInfo, path_config
from api.security.role_enum import RoleEnum
from main import app


def test_get_path_info_basic_case():
    config = EndpointConfig({
        '/test': {
            "GET": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=False),
            "DELETE": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=False)
        },
        '/test/abc': {
            "GET": EndpointInfo(role=RoleEnum.GROUP_CREATOR, has_subroles=True),
            "POST": EndpointInfo(role=RoleEnum.ADMIN, has_subroles=True)
        },
        '/admin': {
            "POST": EndpointInfo(role=RoleEnum.ADMIN, has_subroles=True),
            "PUT": EndpointInfo(role=RoleEnum.ADMIN, has_subroles=True)
        },
        '/user': {
            "GET": EndpointInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=False),
            "PATCH": EndpointInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=True)
        },
        '/public': {
            "GET": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=False)
        },
    })
    
    # Testing normalized INCOMING path
    assert config.get_path_info("/test", "GET") is not None
    assert config.get_path_info("/test", "GET").role == RoleEnum.EXTERNAL
    assert config.get_path_info("/test/", "GET") is not None
    assert config.get_path_info("/test/", "GET").role == RoleEnum.EXTERNAL
    
    assert config.get_path_info("/test/abc", "GET") is not None
    assert config.get_path_info("/test/abc", "GET").role == RoleEnum.GROUP_CREATOR
    assert config.get_path_info("/test/abc/", "GET") is not None
    assert config.get_path_info("/test/abc/", "GET").role == RoleEnum.GROUP_CREATOR
    
    # Tests für die /test Route
    assert config.get_path_info("/test", "GET") is not None
    assert config.get_path_info("/test", "GET").role == RoleEnum.EXTERNAL
    assert config.get_path_info("/test", "DELETE") is not None
    assert config.get_path_info("/test", "POST") is None
    assert config.get_path_info("/test/a", "GET") is None

    # Tests für die /test/abc Route mit Subrollen
    assert config.get_path_info("/test/abc", "GET") is not None
    assert config.get_path_info("/test/abc", "GET").has_subroles is True
    assert config.get_path_info("/test/abc", "GET").role == RoleEnum.GROUP_CREATOR
    assert config.get_path_info("/test/abc", "POST") is not None
    assert config.get_path_info("/test/abc", "POST").role == RoleEnum.ADMIN
    assert config.get_path_info("/test/abc", "DELETE") is None
    assert config.get_path_info("/test/abc/xyz", "GET") is None

    # Tests für die /admin Route
    assert config.get_path_info("/admin", "POST") is not None
    assert config.get_path_info("/admin", "PUT") is not None
    assert config.get_path_info("/admin", "GET") is None
    assert config.get_path_info("/admin/special", "POST") is None

    # Tests für die /user Route
    assert config.get_path_info("/user", "GET") is not None
    assert config.get_path_info("/user", "GET").role == RoleEnum.GROUP_MEMBER
    assert config.get_path_info("/user", "PATCH") is not None
    assert config.get_path_info("/user", "PATCH").role == RoleEnum.GROUP_MEMBER
    assert config.get_path_info("/user", "DELETE") is None
    assert config.get_path_info("/user/profile", "GET") is None

    # Tests für die /public Route
    assert config.get_path_info("/public", "GET") is not None
    assert config.get_path_info("/public", "GET").role == RoleEnum.EXTERNAL
    assert config.get_path_info("/public", "POST") is None
    assert config.get_path_info("/public/extra", "GET") is None

def test_get_path_info_ignore_trailing_slashes(): 
    config = EndpointConfig({
        # Normal
        '/test': {
            "GET": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=False),
            "DELETE": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=False)
        },
        '/test/abc': {
            "GET": EndpointInfo(role=RoleEnum.GROUP_CREATOR, has_subroles=True),
            "POST": EndpointInfo(role=RoleEnum.ADMIN, has_subroles=True)
        },
        # Trailing slashed
        '/configured_with_trailing_slash/': {
            "GET": EndpointInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=False)
        },
        '/configured_with_trailing_slash/sub/': {
            "GET": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=False)
        },
    })
    
    # Testing normalized CONFIGURED path
    assert config.get_path_info("/configured_with_trailing_slash", "GET") is not None
    assert config.get_path_info("/configured_with_trailing_slash", "GET").role == RoleEnum.GROUP_MEMBER
    assert config.get_path_info("/configured_with_trailing_slash/", "GET") is not None
    assert config.get_path_info("/configured_with_trailing_slash/", "GET").role == RoleEnum.GROUP_MEMBER

    assert config.get_path_info("/configured_with_trailing_slash/sub", "GET") is not None
    assert config.get_path_info("/configured_with_trailing_slash/sub", "GET").role == RoleEnum.EXTERNAL
    assert config.get_path_info("/configured_with_trailing_slash/sub/", "GET") is not None
    assert config.get_path_info("/configured_with_trailing_slash/sub/", "GET").role == RoleEnum.EXTERNAL
    
    # Testing normalized INCOMING path
    assert config.get_path_info("/test", "GET") is not None
    assert config.get_path_info("/test", "GET").role == RoleEnum.EXTERNAL
    assert config.get_path_info("/test/", "GET") is not None
    assert config.get_path_info("/test/", "GET").role == RoleEnum.EXTERNAL
    
    assert config.get_path_info("/test/abc", "GET") is not None
    assert config.get_path_info("/test/abc", "GET").role == RoleEnum.GROUP_CREATOR
    assert config.get_path_info("/test/abc/", "GET") is not None
    assert config.get_path_info("/test/abc/", "GET").role == RoleEnum.GROUP_CREATOR
     
def test_get_path_info_variables(): 
    config = EndpointConfig({
        '/a/{test}': {
            "GET": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=False),
            "DELETE": EndpointInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=True)
        },
        '/a/b': {
            "GET": EndpointInfo(role=RoleEnum.GROUP_CREATOR, has_subroles=False),
            "DELETE": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True)
        },
        '/a/b/c': {
            "GET": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=False),
            "DELETE": EndpointInfo(role=RoleEnum.ADMIN, has_subroles=True)
        },
        '/a/b/{c}': {
            "GET": EndpointInfo(role=RoleEnum.EDIT_CREATOR, has_subroles=False),
            "DELETE": EndpointInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=True)
        },
    })
    
    # Tests für Variablenpfade
    assert config.get_path_info("/a/test_value", "GET") is not None
    assert config.get_path_info("/a/test_value", "GET").role == RoleEnum.EXTERNAL
    assert config.get_path_info("/a/test_value", "DELETE") is not None
    assert config.get_path_info("/a/test_value", "DELETE").role == RoleEnum.GROUP_MEMBER

    # Tests für statische Pfade
    assert config.get_path_info("/a/b", "GET") is not None
    assert config.get_path_info("/a/b", "GET").role == RoleEnum.GROUP_CREATOR
    assert config.get_path_info("/a/b", "DELETE") is not None
    assert config.get_path_info("/a/b", "DELETE").role == RoleEnum.EXTERNAL

    # Tests für komplexe Pfade mit Variablen
    assert config.get_path_info("/a/b/c", "GET") is not None
    assert config.get_path_info("/a/b/c", "GET").role == RoleEnum.EXTERNAL
    assert config.get_path_info("/a/b/c", "DELETE") is not None
    assert config.get_path_info("/a/b/c", "DELETE").role == RoleEnum.ADMIN

    assert config.get_path_info("/a/b/some_value", "GET") is not None
    assert config.get_path_info("/a/b/some_value", "GET").role == RoleEnum.EDIT_CREATOR
    assert config.get_path_info("/a/b/some_value", "DELETE") is not None
    assert config.get_path_info("/a/b/some_value", "DELETE").role == RoleEnum.GROUP_MEMBER

def test_get_path_info_exotic_paths():
    config = EndpointConfig({
        '/overlapping/path': {
            "GET": EndpointInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=False),
            "POST": EndpointInfo(role=RoleEnum.ADMIN, has_subroles=True),
        },
        '/overlapping/{param}': {
            "GET": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=False),
            "DELETE": EndpointInfo(role=RoleEnum.ADMIN, has_subroles=True),
        },
        '/very/complex/path/a/{b}/c/{d}': {
            "GET": EndpointInfo(role=RoleEnum.GROUP_CREATOR, has_subroles=False),
            "POST": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True),
        },
        '/very/complex/path/{a}/b/c/{d}/': {
            "GET": EndpointInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=False),
        },
        '/very/complex/path/{a}/{b}/{c}/{d}': {
            "GET": EndpointInfo(role=RoleEnum.ADMIN, has_subroles=False),
        },
    })

    # Test für Pfade mit und ohne Trailing Slashes
    assert config.get_path_info("/overlapping/path", "GET") is not None
    assert config.get_path_info("/overlapping/path/", "GET") is not None
    
    # Überprüfen der spezifischen Rolle bei get_path_info
    assert config.get_path_info("/overlapping/path", "GET").role == RoleEnum.GROUP_MEMBER
    assert config.get_path_info("/overlapping/path/", "GET").role == RoleEnum.GROUP_MEMBER
    
    # Test für einen variablen Pfad
    assert config.get_path_info("/overlapping/test_value", "GET") is not None
    assert config.get_path_info("/overlapping/test_value", "GET").role == RoleEnum.EXTERNAL

    # Test für komplexe Pfade mit Variablen
    assert config.get_path_info("/very/complex/path/a/b/c/d", "GET") is not None
    assert config.get_path_info("/very/complex/path/a/b/c/d", "GET").role == RoleEnum.GROUP_CREATOR
    
    assert config.get_path_info("/very/complex/path/x/b/c/y", "GET") is not None
    assert config.get_path_info("/very/complex/path/x/b/c/y", "GET").role == RoleEnum.GROUP_MEMBER
    
    assert config.get_path_info("/very/complex/path/x/y/z/q", "GET") is not None
    assert config.get_path_info("/very/complex/path/x/y/z/q", "GET").role == RoleEnum.ADMIN

    # Test für POST Methode auf einem komplexen Pfad
    assert config.get_path_info("/very/complex/path/a/b/c/d", "POST") is not None
    assert config.get_path_info("/very/complex/path/a/b/c/d", "POST").role == RoleEnum.EXTERNAL

    # Überprüfen, dass Pfade mit unerwarteten Kombinationen nicht matchen
    assert config.get_path_info("/overlapping/path/something", "GET") is None
    assert config.get_path_info("/very/complex/path/a", "GET") is None
    
  
def test_all_paths_have_role_configuration():
    
    # Alle Routen und Methoden aus dem PROD-Router abrufen
    prod_routes_and_methods = []

    for route in app.router.routes:
        if isinstance(route, Mount):
            # Wenn die Route ein Mount-Objekt ist, durchlaufen Sie die untergeordneten Routen
            for subroute in route.routes:
                prod_routes_and_methods.append((subroute.path, subroute.methods))
        elif isinstance(route, Route):
            # Wenn die Route eine normale Route ist, fügen Sie sie direkt hinzu
            prod_routes_and_methods.append((route.path, route.methods))

    # Überprüfen, ob jede Route in der Konfiguration vorhanden ist
    for path, methods in prod_routes_and_methods:
        for method in methods:
            # Trailing Slash entfernen
            normalized_path = path.rstrip('/')
            # Überprüfen, ob der Pfad in der Konfiguration vorhanden ist
            path_info = path_config.get_path_info(normalized_path, method)
            assert path_info is not None, f"Route {normalized_path} with method {method} is not configured."

    # Überprüfen, dass alle konfigurierten Pfade im Router vorhanden sind
    config_paths = set(path.rstrip('/') for path in path_config.routes.keys())

    # Trailing Slashes aus den App-Pfaden entfernen und ein Set erstellen
    app_paths = set(path.rstrip('/') for path, _ in prod_routes_and_methods)

    # Vergleichen der beiden Sets
    assert app_paths == config_paths, "There are unconfigured paths in the app router or extra paths in the config."