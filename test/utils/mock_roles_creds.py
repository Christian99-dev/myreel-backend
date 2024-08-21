import os
from api.auth import jwt
from api.auth.role_enum import RoleEnum
from test.utils.test_model import group_id_1

# these are example request parameter, simulation the 5 roles. based on the test_model.py

jwt_user_1 = jwt.create_jwt(1, 30)
jwt_user_2 = jwt.create_jwt(2, 30)
    
admin_req_creds = {
    "req": {    
        "headers": {
            "admintoken": str(os.getenv("ADMIN_TOKEN"))
        }
    }, 
    "role": RoleEnum.ADMIN
}

group_creator_req_creds = {
    "req": {    
        "headers": {
            "Authorization": f"Bearer {jwt_user_1}"
        },
        "params": {
            "groupid": group_id_1
        }
    }, 
    "role": RoleEnum.GROUP_CREATOR
}

edit_creator_req_creds = {
    "req": {    
        "headers": {
            "Authorization": f"Bearer {jwt_user_1}"
        },
        "params": {
            "editid": "1"
        }
    }, 
    "role": RoleEnum.EDIT_CREATOR
}

group_member_req_creds = {
    "req": {    
        "headers": {
            "Authorization": f"Bearer {jwt_user_2}"
        },
        "params": {
            "groupid": group_id_1
        }
    }, 
    "role": RoleEnum.GROUP_MEMBER
}

external_req_creds = {
    "req": {
        "headers": {},
        "params": {}
    }, 
    "role": RoleEnum.EXTERNAL
}
