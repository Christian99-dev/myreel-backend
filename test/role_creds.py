import os
from api.utils.jwt import jwt
from api.security.role_enum import RoleEnum
from mock.database.model import group_id_1


jwt_user_1 = jwt.create_jwt(1, 30)
jwt_user_2 = jwt.create_jwt(2, 30)
jwt_user_3 = jwt.create_jwt(3, 30)
    
admin_req_creds = {
    "req": {    
        "headers": {
            "admintoken": str(os.getenv("ADMIN_TOKEN"))
        }
    }, 
    "role": RoleEnum.ADMIN,
    "userid": 1
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
    "role": RoleEnum.GROUP_CREATOR,
    "userid": 1
}

edit_creator_req_creds = {
    "req": {    
        "headers": {
            "Authorization": f"Bearer {jwt_user_2}"
        },
        "params": {
            "editid": "3"
        }
    }, 
    "role": RoleEnum.EDIT_CREATOR,
    "userid": 2
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
    "role": RoleEnum.GROUP_MEMBER,
    "userid": 2
}

external_req_creds = {
    "req": {
        "headers": {},
        "params": {}
    }, 
    "role": RoleEnum.EXTERNAL,
    "userid": 1
}

# 
group_creator_with_edit_id_req_creds = {
    "req": {    
        "headers": {
            "Authorization": f"Bearer {jwt_user_1}"
        },
        "params": {
            "editid": "1"
        }
    }, 
    "role": RoleEnum.GROUP_CREATOR,
    "userid": 1
}

group_member_with_edit_id_req_creds = {
    "req": {    
        "headers": {
            "Authorization": f"Bearer {jwt_user_3}"
        },
        "params": {
            "editid": "1"
        }
    }, 
    "role": RoleEnum.GROUP_MEMBER,
    "userid": 2
}