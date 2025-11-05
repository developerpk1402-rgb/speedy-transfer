class ReportsRouter:
    """
    A router to control database operations for the reporting portal.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read auth models go to reports db.
        """
        if model._meta.app_label == 'auth' and 'reports' in hints.get('instance', ''):
            return 'reports'
        return None

    def db_for_write(self, model, **hints):
        """
        Writes are not allowed to reports db.
        """
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if both objects are in the reports db.
        """
        if obj1._state.db == 'reports' and obj2._state.db == 'reports':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Don't allow migrations on reports db.
        """
        if db == 'reports':
            return False
        return None