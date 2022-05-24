from abc import ABC, abstractmethod
class AbstractDatabaseManager(ABC):
    

    def __init__(self):

        pass

    
    @abstractmethod
    def read_data(self):
        raise NotImplementedError("Database interface not defined.")

    @abstractmethod
    def create_data(self):
        raise NotImplementedError("Database interface not defined.")

    @abstractmethod
    def update_data(self):
        raise NotImplementedError("Database interface not defined.")

    @abstractmethod
    def delete_data(self):
        raise NotImplementedError("Database interface not defined.")