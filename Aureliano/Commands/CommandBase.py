from Commands.Exceptions import BadCommandSyntaxError, BadSyntaxError, UnkownCommandError
from Commands import *
import Commands
from collections import OrderedDict
import sys
import re


##################
# Helper classes #
##################
class Helper:
    def __init__(self, Commando, Help=None):
        self._info = {}
        try:
            self._info["help"] = Commando.getBriefHelp(Commando)
            self._info["name"] = Commando.__name__[3:]
        except AttributeError:
            self._info["name"] = Commando
            """
            try:
                self._info["help"] = Help[0]
            """
            if Help is None:
                #TODO: Extract class and help
                pass
            else:
                self._info["help"] = Help

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "{name: <20}{help}".format(**self._info)


###########################
# Base class for commands #
###########################
class CommandBase(object):
    _BriefHelpStr = "Please implement!"
    SingleParametersRegex = OrderedDict()
    MultiParametersRegex = None
    __RE_WhiteSpace = r'\s+'
    __RE_PossibleWhiteSpace = r'\s*'
    def __init__(self, arguments, Aureliano):
        assert self.__class__.__name__[:3] == "Cmd", "Invalid inheritance! Class name should start with Cmd"
        self._Aureliano = Aureliano
        self.name = self.__class__.__name__[3:]
        self.__parseArguments(arguments)
        #print("{}:{} ({})".format(self.name, repr(arguments), self.Args))

    def __buildArgsRegex(self):
        SingleRegex = None
        for ArgName, ArgRegex in self.SingleParametersRegex.items():
            try:
                SingleRegex = SingleRegex + self.__RE_WhiteSpace + "(?P<{}>".format(ArgName) + ArgRegex + ")"
            except TypeError:
                SingleRegex = "(?P<{}>".format(ArgName) + ArgRegex + ")"
        MultiRegex = None
        try:
            MultiParamREIter = self.MultiParametersRegex.items()
        except AttributeError:
            pass
        else:
            for ArgName, ArgRegex in MultiParamREIter:
                try:
                    MultiRegex = MultiRegex + self.__RE_WhiteSpace + "(?P<{}>".format(ArgName) + ArgRegex + ")"
                except TypeError:
                    MultiRegex = "(?P<{}>".format(ArgName) + ArgRegex + ")"
        finally:
            return SingleRegex, MultiRegex

    def __parseArguments(self, arguments):
        ## One-liner
        if type(arguments) is str:
            ## Automatically build Regex
            SingleRegex, MultiRegex = self.__buildArgsRegex()

            ## Build full Regex
            try:
                CmdRegex = self.__RE_PossibleWhiteSpace + SingleRegex + self.__RE_WhiteSpace + MultiRegex + self.__RE_PossibleWhiteSpace
            except TypeError: #The command has only SingleRegex
                CmdRegex = self.__RE_PossibleWhiteSpace + SingleRegex + self.__RE_PossibleWhiteSpace

            ## Check syntax
            try:
                self.Args = re.match(CmdRegex, arguments).groupdict()
            except AttributeError:
                raise BadCommandSyntaxError(self._Aureliano, self.name, arguments) from None
        ## Multi-line command.
        else:
            ## Check if command is multi-lineable
            if self.MultiParametersRegex is None:
                raise BadSyntaxError(self._Aureliano, "Not a multi-lineable command!") from None

            ## Automatically build Regex
            SingleRegex, MultiRegex = self.__buildArgsRegex()

            ## Parse main command
            try:
                self.Args = re.match(SingleRegex, arguments[0]).groupdict()
            except AttributeError:
                raise BadCommandSyntaxError(self._Aureliano, self.name, arguments[0]) from None

            ## Parse multi-line commands.
            MultiArgs = []
            for arg in arguments[1:]:
                try:
                    MultiArgs.append(re.match(MultiRegex, arg).groupdict())
                except AttributeError:
                    raise BadCommandSyntaxError(self._Aureliano, self.name, arg) from None
            ## Add multi-line commands.
            self.Args.update({"Multi": MultiArgs})

    @staticmethod
    def __dissectCommand(command):
        try:
            command = re.split(r'\s+', command, 1)
        except TypeError:
            mainCmd, param1 = re.split(r'\s+', command[0], 1)
            params = [param1[:-1]]
            for paramN in command[1:-1]:
                params.append(paramN)
            return mainCmd, params
        else:
            try:
                mainCmd, parameters = command
            except ValueError:
                return command[0], ''
            else:
                return mainCmd, parameters

    @classmethod
    def create(Class, Aureliano, command):
        mainCommand, parameters = Class.__dissectCommand(command)
        cmdClassName = "Cmd"+mainCommand.title()
        for cls in Class.__subclasses__():
            if cmdClassName == cls.__name__:
                cmdClass = cls
                return cmdClass(parameters, Aureliano)
        else:
            raise UnkownCommandError(Aureliano, command)

    def run(self):
        raise NotImplementedError("Command '{}' was defined but not properly implemented!".format(self.name))

    def getBriefHelp(self):
        return self._BriefHelpStr

    def _getHelp(self):
        helpList = []
        # Store help in the list if a valid command.
        if self.__name__[:3] == "Cmd":
            helpList.append(Helper(self))
        # Support getting help of children commands.
        if len(self.__subclasses__()) > 0:
            helpList.extend(self.help())
        return helpList

    @classmethod
    def help(Class):
        allHelp = []
        for cmd in Class.__subclasses__():
            allHelp.extend(cmd._getHelp(cmd))
        return allHelp


