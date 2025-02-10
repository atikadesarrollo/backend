class DataLakeModel:
    def __init__(self, id, name, data):
        self.id = id
        self.name = name
        self.data = data

    def save(self):
        # Lógica para guardar el modelo en la base de datos
        pass

    def update(self, **kwargs):
        # Lógica para actualizar el modelo
        for key, value in kwargs.items():
            setattr(self, key, value)

    def delete(self):
        # Lógica para eliminar el modelo de la base de datos
        pass

    @classmethod
    def get_by_id(cls, id):
        # Lógica para obtener un modelo por su ID
        pass

    @classmethod
    def get_all(cls):
        # Lógica para obtener todos los modelos
        pass