from abc import ABC, abstractmethod


class AbstractCommandBase(ABC):
    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    @abstractmethod
    def getCommandName(self):
        raise NotImplementedError

    @abstractmethod
    def getDescription(self):
        raise NotImplementedError

    @abstractmethod
    def getHelp(self):
        raise NotImplementedError
