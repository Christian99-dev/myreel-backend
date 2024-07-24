from test.utils.mock_path_roles import mock_path_roles
from test.utils.mock_roles_creds import admin_req_creds, group_creator_req_creds, group_member_req_creds, external_req_creds, edit_creator_req_creds
import logging
logger = logging.getLogger("testing")

# test config
def test_setup_routes(app_client_mock_routes_middleware):
    assert app_client_mock_routes_middleware.get("/admin_no_subroles").status_code          == 403
    assert app_client_mock_routes_middleware.get("/group_creator_no_subroles").status_code  == 403
    assert app_client_mock_routes_middleware.get("/edit_creator_no_subroles").status_code   == 403
    assert app_client_mock_routes_middleware.get("/group_member_no_subroles").status_code   == 403
    assert app_client_mock_routes_middleware.get("/external_no_subroles").status_code       == 200
    
    assert app_client_mock_routes_middleware.get("/admin_subroles").status_code            == 403
    assert app_client_mock_routes_middleware.get("/group_creator_subroles").status_code    == 403
    assert app_client_mock_routes_middleware.get("/edit_creator_subroles").status_code     == 403
    assert app_client_mock_routes_middleware.get("/group_member_subroles").status_code     == 403
    assert app_client_mock_routes_middleware.get("/external_subroles").status_code         == 200
    
# maintest
def test_endpoints(app_client_mock_routes_middleware):     
    for path in mock_path_roles.keys():
        # logger.debug("\n")
        for current_creds in [admin_req_creds, group_creator_req_creds, edit_creator_req_creds,group_member_req_creds, external_req_creds]: 
            
            # Extrahiere die erforderlichen Details für die Anfrage
            headers = current_creds["req"]["headers"]
            params  = current_creds["req"].get("params", {})
            
            with_subroles = mock_path_roles.get(path).has_subroles
            
            required_role = mock_path_roles.get(path).role
            current_role  = current_creds["role"]

            # Sende die Anfrage an den Endpoint
            response = app_client_mock_routes_middleware.get(path, headers=headers, params=params)

            # Bestimme den erwarteten Statuscode
            if not with_subroles:
                expected_status = 200 if required_role.value == current_role.value else 403
                assert response.status_code == expected_status
            else:
                expected_status = 200 if required_role.value <= current_role.value else 403
            
        