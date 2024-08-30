from fastapi.testclient import TestClient
from api.mock.path_config.mock_path_config import mock_path_config
from api.mock.role_creds.role_creds import admin_req_creds, group_creator_req_creds, edit_creator_req_creds, external_req_creds, group_member_req_creds, group_creator_with_edit_id_req_creds, group_member_with_edit_id_req_creds
import logging
logger = logging.getLogger("testing")
    
# print(mock_path_config.get_all_paths_and_methods());
def test_access_handler_with_subroles(http_client_mocked_path_config: TestClient):     
    for path, method in mock_path_config.get_all_paths_and_methods():
        path_info = mock_path_config.get_path_info(path, method)
        
        # Beispiel für Subrollen (angenommen, es gibt Subrollen für ADMIN)
        for current_creds in [
            admin_req_creds, 
            group_creator_req_creds, 
            edit_creator_req_creds, 
            group_member_req_creds, 
            external_req_creds,
            group_creator_with_edit_id_req_creds,
            group_member_with_edit_id_req_creds
        ]: 
            headers = current_creds["req"]["headers"]
            params  = current_creds["req"].get("params", {})
            with_subroles = path_info.has_subroles
            required_role = path_info.role
            current_role  = current_creds["role"]

            response = http_client_mocked_path_config.get(path, headers=headers, params=params)


            if not with_subroles:
                expected_status = 200 if required_role.value == current_role.value else 403
            else:
                expected_status = 200 if required_role.value >= current_role.value else 403
                
            assert response.status_code == expected_status
            
            