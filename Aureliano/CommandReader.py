from Commands.Exceptions import BadSyntaxError
from abc import ABC, abstractmethod
import warnings
import re


#######################
# Warnings' formating #
#######################
def WarningFormat(message, category, filename, lineno, line=None):
    return "WARNING: " + message.getMessage() + "\n"


warnings.formatwarning = WarningFormat


##################################
# Base class for syntax warnings #
##################################
class BaseAurelianoSyntaxWarning(SyntaxWarning):
    def __init__(self, ParserInfo, *args, **kwargs):
        self.Info = ParserInfo
        super(BaseAurelianoSyntaxWarning, self).__init__(*args, **kwargs)

    def getMessage(self):
        raise NotImplementedError


############
# Warnings #
############
class UnstartedCommentWarning(BaseAurelianoSyntaxWarning):
    def getMessage(self):
        return "Found end of unstarted multiline comment at line {lineno} of \
{filename}.".format(**self.Info.getInfo())


class UnendedCommentWarning(BaseAurelianoSyntaxWarning):
    pass


class UnendedCommandWarning(BaseAurelianoSyntaxWarning):
    pass


#############################
# Class for command's infos #
#############################
class CommandsInfo(object):
    def __init__(self, filename):
        self.source = filename
        self.resetInfo()

    def resetInfo(self):
        self.InfoDict = {"filename": self.source,
                         "multiline": None,
                         "command": None,
                         "lineno": None,
                         }

    def setMultiLine(self, lineno, command):
        self.InfoDict["multiline"] = {"lineno": lineno,
                                      "command": command,
                                      }

    def setInfo(self, lineno, command):
        self.InfoDict["command"] = command
        self.InfoDict["lineno"] = lineno

    def getInfo(self):
        return self.InfoDict

    def getMultiLineInfo(self):
        return self.InfoDict["multiline"]


####################################
# Base class for commands' sources #
####################################
class BaseCommandsSource(ABC):
    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    def __iter__(self):
        for line, lineno in self.getNextLine():
            if line is None:
                self.close()
                return None
            yield line, lineno

    @abstractmethod
    def getNextLine(self):
        raise NotImplementedError

    @abstractmethod
    def close(self):
        raise NotImplementedError


#######################
# File command source #
#######################
class FileSource(BaseCommandsSource):
    def __init__(self, Aureliano, Filename):
        self.Aureliano = Aureliano
        self.Filename = Filename
        self.file = open(Filename, 'r')
        # TODO: Check syntax before executing anything?

    def getNextLine(self):
        lineno = 0
        while self.Aureliano._running:
            line = self.file.readline()
            if line == '':
                return None, lineno
            lineno += 1
            yield line, lineno

    def close(self):
        self.file.close()


##############################
# Interactive command source #
##############################
class InteractiveSource(BaseCommandsSource):
    MsgInteractWelcome = "At your service, sir!"
    MsgInteractExit = "Goodbye, sir!"

    def __init__(self, Aureliano):
        self.Aureliano = Aureliano
        self.Aureliano._say(self.MsgInteractWelcome)
        self.Aureliano._interactive = True

    def getNextLine(self):
        count = 0
        while self.Aureliano._running:
            try:
                command = input("You: ")
                count += 1
                yield command, count
            except KeyboardInterrupt:
                self.Aureliano._say("Couldn't you ask in a nicer way!? How "
                                    "about saying 'bye'!?")
                self.Aureliano._executePersonalCommand("exit")
                yield None, None
        else:
            yield None, None

    def close(self):
        self.Aureliano._say(self.MsgInteractExit)


class CommandReader(object):
    def __init__(self, Aureliano, filename=None):
        if filename:
            self.CmdSource = FileSource(Aureliano, filename)
            self.CmdInfo = CommandsInfo(filename)
        else:
            self.CmdSource = InteractiveSource(Aureliano)
            self.CmdInfo = CommandsInfo("stdin")

    def __iter__(self):
        for command, lineno in self.CmdSource:
            try:
                cmd = self.__analyzeCommand(command, lineno)
            except BaseAurelianoSyntaxWarning as warning:
                warnings.warn(warning)
                cmd = None

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

    def __analyzeCommand(self, command, lineno):
        command = command.strip()

        if command == "#>":
            if self.__InternalAnalysis.multiComment:
                self.__InternalAnalysis.multiComment -= 1
            else:
                self.CmdInfo.setInfo(lineno, command)
                raise UnstartedCommentWarning(self.CmdInfo)

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
            self.CmdInfo.setMultiLine(lineno, command)
            return None
        elif command == "}":
            if self.__InternalAnalysis.final:
                raise BadSyntaxError("End of unstarted multi-line command!") \
                    from None
            self.__InternalAnalysis.final = True
            cmd = list(self.__InternalAnalysis.completeCommand)
            self.__InternalAnalysis.completeCommand = []
            self.CmdInfo.resetInfo()
            return cmd
        else:
            if self.__InternalAnalysis.final:
                self.__InternalAnalysis.completeCommand[:] = []
                self.CmdInfo.resetInfo()
                return command
            else:
                return None
