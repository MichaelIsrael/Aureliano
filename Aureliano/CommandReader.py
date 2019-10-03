from Commands.Exceptions import BadSyntaxError
from abc import ABC, abstractmethod
import re


class BaseCommandsSource(ABC):
    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    def __iter__(self):
        for line in self.getNextLine():
            if line is None:
                self.close()
                return None
            yield line

    @abstractmethod
    def getNextLine(self):
        raise NotImplementedError

    @abstractmethod
    def close(self):
        raise NotImplementedError


class FileSource(BaseCommandsSource):
    def __init__(self, Aureliano, Filename):
        self.Aureliano = Aureliano
        self.file = open(Filename, 'r')
        # TODO: Check syntax before executing anything?

    def getNextLine(self):
        while self.Aureliano._running:
            line = self.file.readline()
            if line == '':
                return None
            yield line

    def close(self):
        self.file.close()


class InteractiveSource(BaseCommandsSource):
    MsgInteractWelcome = "At your service, sir!"
    MsgInteractExit = "Goodbye, sir!"

    def __init__(self, Aureliano):
        self.Aureliano = Aureliano
        self.Aureliano._say(self.MsgInteractWelcome)
        self.Aureliano._interactive = True

    def getNextLine(self):
        while self.Aureliano._running:
            try:
                command = input("You: ")
                yield command
            except KeyboardInterrupt:
                self.Aureliano._say("Couldn't you ask in a nicer way!? How "
                                    "about saying 'bye'!?")
                self.Aureliano._executePersonalCommand("exit")
                yield None
        else:
            yield None

    def close(self):
        self.Aureliano._say(self.MsgInteractExit)


class CommandReader(object):
    def __init__(self, Aureliano, filename=None):
        if filename:
            self.CmdSource = FileSource(Aureliano, filename)
        else:
            self.CmdSource = InteractiveSource(Aureliano)

    def __iter__(self):
        for command in self.CmdSource:
            cmd = self.__analyzeCommand(command)
            if cmd is None:
                continue
            else:
                yield cmd
        return None

    class __CInternalAnalysis:
        final = True
        completeCommand = []
        multiComment = 0

    __InternalAnalysis = __CInternalAnalysis()

    def __analyzeCommand(self, command):
        command = command.strip()

        if command == "#>":
            if self.__InternalAnalysis.multiComment:
                self.__InternalAnalysis.multiComment -= 1
            else:
                print("Warning!")

        if command == "#<":
            self.__InternalAnalysis.multiComment += 1

        if self.__InternalAnalysis.multiComment:
            return None

        command = re.sub("#.*$", "", command)

        if command == "":
            return None

        self.__InternalAnalysis.completeCommand.append(command)

        # Check if multiline.
        if command.endswith("{"):
            if not self.__InternalAnalysis.final:
                raise BadSyntaxError("Nested commands are not yet supported!")\
                    from None
            self.__InternalAnalysis.final = False
            return None
        elif command == "}":
            if self.__InternalAnalysis.final:
                raise BadSyntaxError("End of unstarted multi-line command!") \
                    from None
            self.__InternalAnalysis.final = True
            cmd = list(self.__InternalAnalysis.completeCommand)
            self.__InternalAnalysis.completeCommand = []
            return cmd
        else:
            if self.__InternalAnalysis.final:
                self.__InternalAnalysis.completeCommand[:] = []
                return command
            else:
                return None
