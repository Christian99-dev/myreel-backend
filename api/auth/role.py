class Role:
    def __init__(self, admintoken=None, userid=None, groupid=None, editid=None):
        self._role = "admin" 

    def hasAccess(self, role_string, include_sub_roles=True):
        role_hierarchy = {
            "admin": ["GroupCreator", "EditCreator", "GroupMember", "External"],
            "GroupCreator": ["GroupMember", "External"],
            "EditCreator": ["GroupMember", "External"],
            "GroupMember": ["External"],
            "External": []
        }

        if include_sub_roles:
            if self._role == role_string:
                return True
            elif role_string in role_hierarchy.get(self._role, []):
                return True
            return False
        else:
            return self._role == role_string
