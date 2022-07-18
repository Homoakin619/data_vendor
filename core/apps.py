from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

# class MyAdminConfig(AppConfig):
#     default_site = 'core.admin.MyAdmin'
#     name = 'core.admin.MyAdmin'
    