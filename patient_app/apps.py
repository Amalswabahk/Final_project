from django.apps import AppConfig


class PatientAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'patient_app'


from django.apps import AppConfig

class PatientModuleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'patient_module'

    def ready(self):
        import patient_app.signals
