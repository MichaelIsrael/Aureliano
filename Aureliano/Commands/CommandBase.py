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

class ParametersBuilder(object):
    def __init__(self):
        pass


    def addMain(self, Name, Regex, Optional=False):
        if(Optional):
            raise NotImplementedError

        try:
            self.__MainRegex = self.__MainRegex + r'\s+' + "(?P<{}>".format(Name) + Regex + ")"
        except AttributeError:
            self.__MainRegex = "(?P<{}>".format(Name) + Regex + ")"


    def addExtended(self, Name, Regex, Optional=False):
        if(Optional):
            raise NotImplementedError

        try:
            self.__MultiRegex = self.__MultiRegex + r'\s+' + "(?P<{}>".format(Name) + Regex + ")"
            self.__GroupedMultiRegex = self.__GroupedMultiRegex + r'\s+' + Regex
        except AttributeError:
            self.__MultiRegex = "(?P<{}>".format(Name) + Regex + ")"
            self.__GroupedMultiRegex = "(?P<Multi>" + Regex


    def getMainRegex(self):
        return self.__MainRegex


    def getExtendedRegex(self):
        try:
            return self.__GroupedMultiRegex, self.__MultiRegex
        except AttributeError:
            return None, None


    def finalize(self):
        try:
            self.__GroupedMultiRegex = self.__GroupedMultiRegex + ")"
        except AttributeError:
            pass


###########################
# Base class for commands #
###########################
class CommandBase(object):
    _BriefHelpStr = "Please implement!"

    def __init__(self, arguments, Aureliano):
        assert self.__class__.__name__[:3] == "Cmd", "Invalid inheritance! Class name should start with Cmd"
        self._Aureliano = Aureliano
        self.name = self.__class__.__name__[3:]
        self.__createRegexes()
        self.__parseArguments(arguments)


    def __createRegexes(self):
        self.Parameters = ParametersBuilder()

        self.addMainParameter = self.Parameters.addMain
        self.addExtendedParameter = self.Parameters.addExtended

        self.registerParameters()

        self.Parameters.finalize()


    def registerParameters(self):
        raise NotImplementedError("Command '{}' was defined but not properly implemented!".format(self.name))


    def __parseArguments(self, arguments):
        ## Automatically build Regex
        #SingleRegex, GroupedMultiRegex, MultiRegex = self.__buildArgsRegex()
        SingleRegex = self.Parameters.getMainRegex()
        GroupedMultiRegex, MultiRegex = self.Parameters.getExtendedRegex()

        ## One-liner
        if type(arguments) is str:
            ## Build full Regex
            try:
                CmdRegex = r'\s*' + SingleRegex + r'\s+' + GroupedMultiRegex + r'\s*'
            except TypeError: #The command has only SingleRegex
                CmdRegex = r'\s*' + SingleRegex + r'\s*'

            ## Check syntax
            try:
                self.Args = re.match(CmdRegex, arguments).groupdict()
            except AttributeError:
                raise BadCommandSyntaxError(self._Aureliano, self.name, arguments) from None

            try:
                MultiParameters = self.Args.pop("Multi")
                MultiArgs = re.match(MultiRegex, MultiParameters).groupdict()
                self.Args["Multi"] = [MultiArgs]
            except AttributeError:
                raise BadCommandSyntaxError(self._Aureliano, self.name, arguments) from None
        else: ## Multi-line command.
            ## Check if command is multi-lineable
            if MultiRegex is None:
                raise BadSyntaxError(self._Aureliano, "Not a multi-lineable command!") from None

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


