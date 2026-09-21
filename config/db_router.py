class CPJRouter:

    def db_for_read(self, model, **hints):
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'cpj':
            return 'cpj'

        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'cpj':
            return False

        return None