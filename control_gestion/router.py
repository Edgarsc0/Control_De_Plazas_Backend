class ControlGestionRouter:
    """
    Un router para controlar todas las operaciones de base de datos en los
    modelos de la aplicación control_gestion.
    """
    route_app_labels = {'control_gestion'}

    def db_for_read(self, model, **hints):
        """
        Las lecturas de control_gestion van a la base de datos control_gestion.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'control_gestion'
        return None

    def db_for_write(self, model, **hints):
        """
        Las escrituras de control_gestion van a la base de datos control_gestion.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'control_gestion'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Permitir relaciones si alguno de los modelos involucrados es de control_gestion.
        """
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Asegurarse de que la app control_gestion solo aparezca en la base 'control_gestion'.
        """
        if app_label in self.route_app_labels:
            return db == 'control_gestion'
        return None
