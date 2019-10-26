from Commands.Exceptions import BadCommandSyntaxError, UnkownCommandError
from Commands.Helper import Helper
from Commands.AbstractCommandBase import AbstractCommandBase
from abc import abstractmethod
import re


#######################
# Internal exceptions #
#######################
class InvalidCommandClass(Exception):
    def __init__(self, klass):
        self._class = klass


class InvalidClassName(InvalidCommandClass):
    def __str__(self):
        return "{} is not a valid command class name.".format(
            self._class.__name__)


class NotACommandSubclass(InvalidCommandClass):
    def __str__(self):
        return "Class {} is not a subclass of ExternalCommandBase.".format(
            self._class.__name__)


#####################################
# Parameter help generation classes #
#####################################
class ParametersHelp(object):
    def __init__(self, Name, Help):
        self.Name = Name
        self.Help = Help
        self.Parameters = {}

    def addParameterHelp(self, Name, Help):
        self.Parameters[Name] = Help

    def getHelp(self):
        return "TODO: Help for {}.".format(self.Name,
                                           " and ".join(self.Parameters.keys())
                                           )


class HelpIterator(object):
    def __init__(self, Parameters):
        self.Parameters = Parameters

    def __iter__(self):
        self.idx = -1
        return self

    def __next__(self):
        self.idx += 1
        try:
            return ParametersHelp(self.Parameters[self.idx]).getHelp()
        except IndexError:
            raise StopIteration from None


################################
# Parameter generation classes #
################################
class ParametersGroup(object):
    def __init__(self, Name, Help, Greedy=False):
        self.Name = Name
        self.Help = Help
        self._Greedy = Greedy
        self._ready = False
        self._OptionalParameters = False

        self._Regex = "(?P<FullCommand>(?P<Command>(?i){})".format(Name)

    def addParameter(self, Name, Regex, Help="", Optional=False):
        Suffix = r''
        Spacer = r'\s+'
        if(Optional):
            self._OptionalParameters = True
        else:
            if Optional is False and self._OptionalParameters:
                raise NotImplementedError  # TODO: A meaningful exception.

        if self._OptionalParameters:
            Spacer = r'\s*'
            Suffix = r'?'

        self._Regex += Spacer \
            + r'(?P<{}>\b'.format(Name) \
            + Regex \
            + r'\b)' \
            + Suffix

    def getRegex(self):
        assert self._ready, "Internal error: ParametersGroup '{}' was not \
                             finalized!".format(self.Name)
        return self._Regex

    def finalize(self):
        if self._Greedy:
            self._Regex += r"(\s*(?P<Extra>\S.*))?"
        self._Regex += ")$"
        self._ready = True

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return self.getRegex()


class ParametersBuilder(object):
    def __init__(self, name):
        self._OptionalMainParameter = False
        self.MainGroup = ParametersGroup(name.lower(), "TODO", True)
        self.ExtendedGroups = []

    def getMainRegex(self):
        return self.MainGroup.getRegex()

    def getExtendedRegex(self):
        Regex = "({})".format('|'.join(self))
        return Regex

    def newExtendedGroup(self, *args, **kwargs):
        newGroup = ParametersGroup(*args, **kwargs)
        self.ExtendedGroups.append(newGroup)
        return newGroup

    def finalize(self):
        self.MainGroup.finalize()
        for Group in self.ExtendedGroups:
            Group.finalize()

    def __iter__(self):
        return iter([str(grp) for grp in self.ExtendedGroups])

    def getHelp(self):
        AllParameters = [self.MainGroup].extend(self.ExtendedGroups)
        return iter(HelpIterator(AllParameters))


###########################
# Base class for commands #
###########################
class ExternalCommandBase(AbstractCommandBase):
    def __init__(self, arguments=None):
        self.EnsureValidity(self.__class__)

        self.Name = self.__class__.__name__[3:]

        self.__createRegexes()

        # TODO: Separate the arguments from the initialization?
        if arguments:
            self.__parseArguments(arguments)

    @staticmethod
    def EnsureValidity(cls):
        if not issubclass(cls, ExternalCommandBase):
            raise NotACommandSubclass(cls)

        prefix = cls.__name__[:3]
        name = cls.__name__[3:]
        if prefix != "Cmd" or name != name.title():
            raise InvalidClassName(cls)

    def getDescription(self):
        """Get the description of the command.
        Returns:
          A str describing the command.
        """
        raise NotImplementedError("Please describe your command!")

    def getCommandName(self):
        return self.Name

    def __createRegexes(self):
        self.Parameters = ParametersBuilder(self.Name)

        self.addMainParameter = self.Parameters.MainGroup.addParameter
        self.createExtendedParametersGroup = self.Parameters.newExtendedGroup

        self.registerParameters()

        self.Parameters.finalize()

    @abstractmethod
    def registerParameters(self):
        raise NotImplementedError("Command '{}' was defined but not properly \
                                   implemented!".format(self.Name))

    def __parseArguments(self, arguments):
        # get Regexes
        MainRegex = self.Parameters.getMainRegex()
        ExtendedRegex = self.Parameters.getExtendedRegex()

        # Check syntax
        try:
            # One-liner
            self.Args = re.match(MainRegex, arguments).groupdict()
            ExtendedArgs = [self.Args.pop("Extra")]
        except AttributeError:
            raise BadCommandSyntaxError(self, arguments) from None
        except TypeError:  # Multi-line command.
            # Parse main command
            try:
                self.Args = re.match(MainRegex, arguments[0]).groupdict()
            except AttributeError:
                raise BadCommandSyntaxError(self, arguments[0]) from None

            assert self.Args["Extra"] is None, \
                "Unexpected arguments {} in a multiline call.".format(
                    self.Args["Extra"])

            ExtendedArgs = arguments[1:]

        ExtendedCommands = []
        # Parse multi-line commands.
        for arg in ExtendedArgs:
            for ExtendedRegex in self.Parameters:
                try:
                    ExtendedCommands.append(re.match(ExtendedRegex,
                                                     arg).groupdict())
                except AttributeError:
                    continue
                break
            else:
                raise BadCommandSyntaxError(self, arg) from None
        # Add multi-line commands.
        self.Args.update({"Extended": ExtendedCommands})

    @staticmethod
    def __dissectCommand(FullCommand):
        # TODO: This should be moved to CommandReader!!!
        print(FullCommand)
        try:
            command = re.split(r'\s+', FullCommand, 1)[0]
            arguments = FullCommand
        except TypeError:
            command = re.split(r'\s+', FullCommand[0], 1)[0]
            arguments = [FullCommand[0][:-1]]
            arguments.extend(FullCommand[1:-1])
        finally:
            print(command, arguments)
            return command, arguments

    @classmethod
    def create(cls, command):
        CmdName, parameters = cls.__dissectCommand(command)
        cmdClass = cls.getCommand(CmdName)
        return cmdClass(parameters)

    @classmethod
    def getCommand(cls, CommandName):
        """Get the command's class

        Args:
            CommandName (str): Command.

        Returns:
            class of the command required.

        Raises:
            UnkownCommandError: If the command was not found.
        """
        # Construct command name according to the predefined scheme.
        ClassName = "Cmd" + str(CommandName).title()
        try:
            # Get the class if it exists.
            CmdClass = globals()[ClassName]
        except KeyError:
            raise UnkownCommandError(CommandName) from None
        else:
            # Make sure it is a subclass of the current class.
            if not issubclass(CmdClass, cls):
                raise UnkownCommandError(CommandName) from None
            else:
                return CmdClass

    @abstractmethod
    def run(self):
        raise NotImplementedError("Command '{}' was defined but not properly \
                                   implemented!".format(self.Name))

    @classmethod
    def help(cls):
        allHelp = []
        for cmd in cls.__subclasses__():
            try:
                cls.EnsureValidity(cmd)
            except InvalidClassName:
                pass
            else:
                allHelp.append(Helper(cmd()))

            if len(cmd.__subclasses__()) > 0:
                allHelp.extend(cmd.help())
        return allHelp

    def getHelp(self):
        for Help in self.Parameters.getHelp():
            print(Help)
        raise NotImplementedError("Full help for {}".format(self.Name))
