from api.security.endpoints_class import EndpointConfig, EndpointInfo
from api.security.role_enum import RoleEnum

endpoint_config = EndpointConfig({
    
    # fastapi
    '/openapi.json':{
        "GET": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True), 
        "HEAD": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True)
    },

    '/docs':{
        "GET": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True), 
        "HEAD": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True)
    },

    '/docs/oauth2-redirect':{
        "GET": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True), 
        "HEAD": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True)
    },

    '/redoc':{
        "GET": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True), 
        "HEAD": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True)
    },
    
    # root 
    '/':                                   {"GET": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},

    # Static routes
    '/files/covers/{filename}':           {"GET": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},
    '/files/demo_slot/{filename}':        {"GET": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},
    '/files/edits/{filename}':            {"GET": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},
    '/files/occupied_slots/{filename}':   {"GET": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},
    '/files/songs/{filename}':            {"GET": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},
    
    # testroutes
    '/testing/1':            {"GET": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},
    '/testing/2':            {"GET": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},
    '/testing/3':            {"GET": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},
    '/testing/4':            {"GET": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},
    
    # song
    '/song/':                            {"POST":   EndpointInfo(role=RoleEnum.ADMIN, has_subroles=True)},
    '/song/{song_id}':                   {
                                            "DELETE": EndpointInfo(role=RoleEnum.ADMIN, has_subroles=True),
                                            "GET":    EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True)
                                         },
    '/song/list':                        {"GET":    EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},
    
    # group
    '/group':                           {"POST": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},
    '/group/{group_id}':                {
                                            "GET": EndpointInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=True),
                                            "DELETE": EndpointInfo(role=RoleEnum.GROUP_CREATOR, has_subroles=True)
                                        },
    '/group/{group_id}/members':        {"GET": EndpointInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=True)},   
    '/group/{group_id}/edits':          {"GET": EndpointInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=True)},   
    '/group/{group_id}/name':           {"GET": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},   

    # user
    '/user/invite':                     {"POST": EndpointInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=True)},    
    '/user/acceptInvite':               {"POST": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},    
    '/user/loginRequest':               {"POST": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},    
    '/user/login':                      {"POST": EndpointInfo(role=RoleEnum.EXTERNAL, has_subroles=True)},    
    
    # edit
    '/edit/{edit_id}/goLive':           {"POST": EndpointInfo(role=RoleEnum.GROUP_CREATOR, has_subroles=True)},    
    '/edit/{edit_id}':                  {
                                            "DELETE": EndpointInfo(role=RoleEnum.GROUP_CREATOR, has_subroles=True),
                                            "GET": EndpointInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=True)
                                        },    
    '/edit/':                           {"POST": EndpointInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=True)},    

    # slot
    '/edit/{edit_id}/slot/{slot_id}' : {
        "POST": EndpointInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=True),
    },
    '/edit/{edit_id}/slot/{slot_id}/preview' : {
        "POST": EndpointInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=True),
    },
    '/edit/{edit_id}/slot/{occupied_slot_id}' : {
        "PUT": EndpointInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=True),
        "DELETE": EndpointInfo(role=RoleEnum.GROUP_MEMBER, has_subroles=True),
    }

})