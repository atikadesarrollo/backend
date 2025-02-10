class OdooModel:
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

    def save(self):
        # Lógica para guardar el modelo en la base de datos
        pass

    @classmethod
    def get_all(cls):
        # Lógica para obtener todos los registros del modelo
        pass

    @classmethod
    def get_by_id(cls, id):
        # Lógica para obtener un registro por ID
        pass

    def update(self, name=None, description=None):
        # Lógica para actualizar el modelo
        pass

    def delete(self):
        # Lógica para eliminar el modelo
        pass