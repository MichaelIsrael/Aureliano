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
            self._info["name"] = Commando.__name__[3:]
        except AttributeError:
            try:
                Help, Params = Help
            except ValueError:
                Params = ""
            finally:
                self._info["name"] = "[{}] {}".format("|".join(Commando), Params).strip()
                if len(self._info["name"]) >= 20:
                    self._info["help"] = "\n" + " "*20 + Help
                else:
                    self._info["help"] = Help
        else:
            try:
                self._info["help"] = Commando.getBriefHelp(Commando)
            except AttributeError:
                self._info["help"] = Help

    def __str__(self):
        return repr(self)

    def __repr__(self):
        """
        if len(self._info["name"]) >= 20:
            return "{name:}\n{help}".format(**self._info)
        else:
        """
        if True:
            return "{name: <20}{help}".format(**self._info)


class ParametersGroup(object):
    def __init__(self, Name, Help, Greedy=False):
        self.Name = Name
        self.Help = Help
        self._Greedy = Greedy
        self._ready = False
        self._OptionalParameters = False

        self._Regex = "(?P<FullCommand>(?P<Command>{})".format(Name)

    def addParameter(self, Name, Regex, Help="", Optional=False):
        Suffix = r''
        Spacer = r'\s+'
        if(Optional):
            self._OptionalParameters = True
        else:
            if Optional is False and self._OptionalParameters:
                raise NotImplementedError

        if self._OptionalParameters:
            Spacer = r'\s*'
            Suffix = r'?'

        self._Regex += Spacer + r'(?P<{}>\b'.format(Name) + Regex + r'\b)' + Suffix

    def getRegex(self):
        assert self._ready, "Internal error: ParametersGroup '{}' was not finalized!".format(self.Name)
        try:
            return self._Regex
        except AttributeError:
            return None

    def finalize(self):
        if self._Greedy:
            self._Regex += "(\s*(?P<Extra>\S.*))?"
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
        #newGroup = ParametersGroup(Name, Help)
        newGroup = ParametersGroup(*args, **kwargs)
        self.ExtendedGroups.append(newGroup)
        return newGroup


    def finalize(self):
        self.MainGroup.finalize()
        for Group in self.ExtendedGroups:
            Group.finalize()

    def __iter__(self):
        return iter([str(grp) for grp in self.ExtendedGroups])


###########################
# Base class for commands #
###########################
class CommandBase(object):
    _BriefHelpStr = "Please implement!"

    def __init__(self, arguments, Aureliano):
        assert self.__class__.__name__[:3] == "Cmd", "Invalid inheritance! Class name should start with Cmd"
        self._Aureliano = Aureliano
        self.name = self.__class__.__name__[3:]
        try:
            self.__createRegexes()
            self.__parseArguments(arguments)
        except BadCommandSyntaxError:
            raise
        except:
            raise Exception("Implementation error!")


    def __createRegexes(self):
        self.Parameters = ParametersBuilder(self.name)

        self.addMainParameter = self.Parameters.MainGroup.addParameter
        self.createExtendedParametersGroup = self.Parameters.newExtendedGroup

        self.registerParameters()

        self.Parameters.finalize()


    def registerParameters(self):
        raise NotImplementedError("Command '{}' was defined but not properly implemented!".format(self.name))


    def __parseArguments(self, arguments):
        ## get Regexes
        MainRegex = self.Parameters.getMainRegex()
        ExtendedRegex = self.Parameters.getExtendedRegex()

        ## Check syntax
        try:
            ## One-liner
            self.Args = re.match(MainRegex, arguments).groupdict()
            ExtendedArgs = [self.Args.pop("Extra")]
        except AttributeError:
                raise BadCommandSyntaxError(self._Aureliano, self.name, arguments) from None
        except TypeError: ## Multi-line command.
            ## Parse main command
            try:
                self.Args = re.match(MainRegex, arguments[0]).groupdict()
            except AttributeError:
                raise BadCommandSyntaxError(self._Aureliano, self.name, arguments[0]) from None

            assert self.Args["Extra"] is None, "Unexpected arguments {} in a multiline call.".format(self.Args["Extra"])

            ExtendedArgs = arguments[1:]

        ExtendedCommands = []
        ## Parse multi-line commands.
        for arg in ExtendedArgs:
            for ExtendedRegex in self.Parameters:
                try:
                    ExtendedCommands.append(re.match(ExtendedRegex, arg).groupdict())
                except AttributeError:
                    continue
                break
            else:
                raise BadCommandSyntaxError(self._Aureliano, self.name, arg) from None
        ## Add multi-line commands.
        self.Args.update({"Extended": ExtendedCommands})


    @staticmethod
    def __dissectCommand(FullCommand):
        try:
            command = re.split(r'\s+', FullCommand, 1)[0]
            arguments = FullCommand
        except TypeError:
            command = re.split(r'\s+', FullCommand[0], 1)[0]
            arguments = [FullCommand[0][:-1]]
            arguments.extend(FullCommand[1:-1])
        finally:
            return command, arguments

    @classmethod
    def create(Class, Aureliano, command):
        CmdName, parameters = Class.__dissectCommand(command)
        cmdClassName = "Cmd"+CmdName.title()
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


