from time import time


class Message():
    def __init__(self,command: str,data,sender) -> None:
        self.__command = command
        self.__data = data
        self.__sender = sender
        self.__time_stamp : float = time()

    @property
    def command(self) -> str:
        return self.__command
    
    @property
    def data(self)-> str:
        return self.__data
    
    @property 
    def sender(self):
        return self.__sender

    @property
    def time_stamp(self)-> float:
        return self.__time_stamp