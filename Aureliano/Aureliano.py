#!/usr/bin/env python3
from Commands.Exceptions import BadCommandSyntaxError
from Commands.AbstractCommandBase import AbstractCommandBase
from ExceptionBase import AurelianoBaseError
from CommandReader import CommandReader
from Commands.Helper import Helper
from Commands import ExternalCommandBase
from time import sleep
import argparse
import random
import copy
import sys
import os
import re


#############
# Constants #
#############
MyName = os.path.splitext(os.path.basename(__file__))[0]
MyVersion = 1.0
MyAuthor = "Michael Israel"


############
# Messages #
############
MsgInsults = ["Are you crazy?",
              "You must be out of your mind!",
              "Impossible, sweet cheeks!",
              "How about we stop messing around and get to work!?",
              "Don't be ridiculous!",
              "Think again, Einstein!",
              "No time for silly jokes, sir!",
              ]


##############################
# Class for inernal commands #
##############################
class InternalCommandBase(AbstractCommandBase):
    def __init__(self, names, func, Parameters, Description):
        self._InternalName = None  # Added by Aureliano in __init__.
        self._CmdNames = names
        self._func = func
        self._Description = Description
        self._Parameters = Parameters

    def getCommandName(self):
        if self._InternalName:
            return self._InternalName
        else:
            return self._CmdNames[0]

    def getHelp(self):
        if self._Parameters:
            Syntax = "({}) {}".format("|".join(self._CmdNames),
                                      self._Parameters)
        else:
            Syntax = "({})".format("|".join(self._CmdNames))

        return Syntax + r"\n    " + self._func.__doc__

    def getDescription(self):
        return self._Description

    def __call__(self, *args):
        self._func(self, *args)


#############
# Aureliano #
#############
class Aureliano:
    def __init__(self):
        self._running = True
        self._interactive = False
        self.__discipline = {
            "verbose": True,  # TODO: is this even used anywhere?
                              # Should be removed or implemented?
            "continue": False,
            "polite": False}

        self._internalCommands = {name: self.__class__.__dict__[name]
                                  for name in self.__class__.__dict__.keys()
                                  if "_Aureliano__Cmd" in name}

        for _, intCommand in self._internalCommands.items():
            for CmdName in intCommand._CmdNames:
                cmdFuncName = "_Cmd" + CmdName.title()
                NewCmd = copy.copy(intCommand)
                setattr(NewCmd, "_InternalName", CmdName)
                setattr(self, cmdFuncName, NewCmd)

    def help(self):
        print("{name} {version} at your command!".format(name=MyName,
                                                         version=MyVersion))
        print(self.getHelpStr())

    def getHelpStr(self):
        # Print internal commands' help
        helpStr = "  Internal commands:"
        for _, intCmd in self._internalCommands.items():
            helpStr += "\n" + re.sub("^",
                                     "    ",
                                     str(Helper(intCmd)),
                                     flags=re.MULTILINE)
        helpStr += "\n"

        # Print external commands:
        helpStr += "\n" + "  External commands:"
        for HelpItem in ExternalCommandBase.help():
            helpStr += "\n" + "    " + str(HelpItem)

        return helpStr

    def _whisper(self, *args):
        if self._interactive:
            msg = "Aureliano: " + str(*args)
        else:
            msg = "Aureliano: " + str(*args)
            # raise NotImplementedError # TODO
        return msg

    def _say(self, *args):
        if self._interactive:
            print(self._whisper(*args))
        else:
            print(self._whisper(*args))
            # raise NotImplementedError # TODO

    def _insult(self):
        """Print insult if default impolite mode is on."""
        if not self.__discipline["polite"]:
            self._say(random.choice(MsgInsults))

    def _handle(self, exception):
        """Let Aureliano handle the exception his way."""
        # This is an error, so insult.
        self._insult()

        # If the application should keep going, just let Aureliano say the
        # error.
        if self.__discipline["continue"] or self._interactive:
            self._say(exception.getNiceName() + ": " + str(exception))
        else:
            # Otherwise, raise the exception and end the application.
            raise exception from None

    def execute(self, command):
        """
        Run a command.
        """
        try:  # First treat as an internal command.
            # Multi-line commands would raise an AttributeError, same as if
            # the command does not exist.
            CmdParameters = command.split()
            CmdName = CmdParameters.pop(0)
            # get internal command.
            IntCommand = self._getInternalCommand(CmdName)
        except AttributeError:  # Try as an external command.
            try:
                # Execute as external command.
                cmd = ExternalCommandBase.create(self, command)
                returncode = cmd.run()
                # Check for execution errors.
                if (not self.__discipline["continue"]
                        and returncode not in [True, None, 0]):
                    self._running = False
            except AurelianoBaseError as e:
                # Handle Aureliano's exceptions nicely.
                self._handle(e)
            except Exception as e:
                # Reraise other exceptions but suppress the personal
                # command's AttributeError.
                raise e from None
        else:
            # Execute the internal command.
            try:
                # Execute as internal command.
                IntCommand(self, *CmdParameters)
            except TypeError:  # TypeErrors usually occur with syntax problems.
                try:
                    # Override exception in a more meaningful way.
                    raise BadCommandSyntaxError(IntCommand,
                                                " ".join(CmdParameters)) \
                        from None
                except AurelianoBaseError as e:
                    # Now cache the new exception and handle it nicely.
                    self._handle(e)
            except AurelianoBaseError as e:
                # Now cache the new exception and handle it nicely.
                self._handle(e)

    def interact(self, Filename=None):
        # Read commands.
        for command in CommandReader(self, Filename):
            self.execute(command)

    def _getInternalCommand(self, command):
        """Get instance of internal command.

        Args:
          command (str): command name.

        Returns:
          A callable instance of the internal command.

        Raises:
          AttributeError: If the command does not exist.
        """
        cmdMethodName = "_Cmd" + command.title()
        return getattr(self, cmdMethodName)

    ###################################
    # Decorator for defining commands #
    ###################################
    def _DefineCommand(Help, *names):
        def command(_Cmd):
            try:
                Description, Parameters = Help
            except ValueError:
                Description = Help
                Parameters = None

            return InternalCommandBase(names, _Cmd, Parameters, Description)

        return command

    #################################
    # Aureliano's internal commands #
    #################################
    @_DefineCommand("Exit.", "Exit", "Bye", "Ciao", "End", "Stop")
    def __Cmd1(CmdSelf, Aureliano):
        """Exit Aureliano."""
        Aureliano._running = False

    @_DefineCommand(("Sleep for a specific time.", "TIME"),
                    "Sleep", "Wait", "Delay")
    def __Cmd2(CmdSelf, Aureliano, time):
        """
        Sleep for a certain amount (TIME) of seconds.
        Arguments:
            TIME    Number of seconds to sleep (float).
        """
        try:
            sleep(float(time))
        except ValueError:
            raise BadCommandSyntaxError(CmdSelf, time) from None

    @_DefineCommand(("Set a certain mode.", "MODE"), "Be", "Become")
    def __Cmd3(CmdSelf, Aureliano, state):
        States = {("quiet", "silent"): ("verbose", False),
                  ("verbose", "talkative"): ("verbose", True),
                  ("polite"): ("polite", True),
                  ("impolite"): ("polite", False),
                  ("persistent"): ("continue", True),
                  ("surrendering"): ("continue", False)}

        for knownState in States.keys():
            if state in knownState:
                Aureliano.__discipline[States[knownState][0]] = \
                    States[knownState][1]
                break
        else:
            raise BadCommandSyntaxError(CmdSelf, state) from None

    @_DefineCommand(("Print help.", "[CMD]"), "Help")
    def __Cmd4(CmdSelf, Aureliano, Command=None):
        """
        Show help.
        If a valid command name is given as an argument to 'help', its full
        specfic help is given.
        """
        if Command:
            try:
                CmdClass = Aureliano._getInternalCommand(Command)
            except AttributeError:
                CmdClass = ExternalCommandBase.getCommand(Command)

            helper = Helper(CmdClass)
            print(helper.getFullHelp())
        else:
            Aureliano.help()

    @_DefineCommand(("Set debug mode.", "MODE"), "debug")
    def __Cmd5(CmdSelf, Aureliano, Mode):
        """
        Set a certain debug mode (show full stack trace of an exception).
        Arguments:
          MODE  either on or off.
        """
        Modes = {"on": 1000, "off": 0}

        Mode = Mode.lower()

        sys.tracebacklimit = Modes[Mode]


if __name__ == "__main__":
    TheColonel = Aureliano()

    parser = argparse.ArgumentParser(
        prog=MyName,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=TheColonel.getHelpStr())

    # -v
    parser.add_argument("-v",
                        "--verbose",
                        help="increase output verbosity.",
                        action="store_true")
    # -p
    parser.add_argument("-p",
                        "--polite",
                        help="No foul language.",
                        action="store_true")
    # -c
    parser.add_argument("-c",
                        "--continue",
                        help="keep going if an error occurs.",
                        action="store_true",
                        dest="cont")

    # -d
    parser.add_argument("-d",
                        "--debug",
                        help="Activate debug mode (show full exceptions).",
                        action="store_true",
                        dest="debug")

    group = parser.add_mutually_exclusive_group()
    # -r
    group.add_argument("-r",
                       "--run",
                       help="Run one command.",
                       nargs='+',
                       metavar="CMD")
    # Commands file.
    group.add_argument("-f",
                       "--filename",
                       help="Name of a text file containing Aureliano \
                             commands to be executed.")

    args = parser.parse_args()

    if args.debug:
        TheColonel.execute("debug on")
    else:
        TheColonel.execute("debug off")

    if args.cont:
        TheColonel.execute("be persistent")

    if args.polite:
        TheColonel.execute("be polite")

    if args.verbose:
        TheColonel.execute("be verbose")

    if args.run:
        TheColonel.execute(" ".join(args.run))
    elif args.filename:
        TheColonel.interact(args.filename)
    else:
        TheColonel.interact()
