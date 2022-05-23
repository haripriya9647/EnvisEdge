from abc import ABC, abstractMethod

class AbstractDatabaseManager(ABC):
    

    def __init__(self):

        pass

    
    @abstractMethod
    def read_data(self):
        raise NotImplementedError("Database interface not defined.")

    @abstractMethod
    def create_data(self):
        raise NotImplementedError("Database interface not defined.")

    @abstractMethod
    def update_data(self):
        raise NotImplementedError("Database interface not defined.")

    @abstractMethod
    def delete_data(self):
        raise NotImplementedError("Database interface not defined.")

