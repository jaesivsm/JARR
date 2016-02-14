from flask.ext.principal import Permission, RoleNeed


admin_role = RoleNeed('admin')
api_role = RoleNeed('api')

admin_permission = Permission(admin_role)
