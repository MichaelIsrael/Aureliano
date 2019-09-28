#!/usr/bin/env python3
from Commands.Exceptions import BadCommandSyntaxError, BadSyntaxError
from Commands.AbstractCommandBase import AbstractCommandBase
from ExceptionBase import AurelianoBaseError
from CommandReader import CommandReader
from Commands.Helper import Helper
from Commands import ExternalCommandBase
from time import sleep
import argparse
import random
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
    def __init__(self, names, func, Parameters, HelpStr):
        self._CmdNames = names
        self._func = func
        self._Help = HelpStr
        self._Parameters = Parameters

    def getCommandName(self):
        return "({}) {}".format("|".join(self._CmdNames), self._Parameters)

    def getBriefHelp(self):
        return self._Help

    def __call__(self, *args):
        self._func(*args)


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
                setattr(self, cmdFuncName, intCommand)

    def execute(self, command):
        """
        Run a command.
        """
        cmd = ExternalCommandBase.create(self, command)
        return cmd.run()

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
        if not self.__discipline["polite"]:
            self._say(random.choice(MsgInsults))

    def _handle(self, exception):
        self._insult()
        if self.__discipline["continue"] or self._interactive:
            self._say(exception)
        else:
            raise exception from None

    def interact(self, Filename=None):
        for command in CommandReader(self, Filename):
            try:
                self._executePersonalCommand(command)
            except TypeError:
                try:
                    raise BadCommandSyntaxError(command) from None
                except BadCommandSyntaxError as e:
                    self._handle(e)
            except AttributeError:
                try:
                    returncode = self.execute(command)
                    if (not self.__discipline["continue"]
                            and returncode not in [True, None, 0]):
                        break
                except AurelianoBaseError as e:
                    self._handle(e)

    def _executePersonalCommand(self, command):
        # Multi-line commands would raise an AttributeError, same as if
        # the command does not exist.
        command = command.split()
        cmdMethodName = "_Cmd" + command[0].title()
        cmdMethod = getattr(self, cmdMethodName)
        return cmdMethod(self, *command[1:])

    ###################################
    # Decorator for defining commands #
    ###################################
    def _DefineCommand(Help, *names):
        def command(_Cmd):
            try:
                HelpStr, Parameters = Help
            except ValueError:
                HelpStr = Help
                Parameters = None

            IntCmd = InternalCommandBase(names, _Cmd, Parameters, HelpStr)

            def commandWrapper(self, *args):
                # Note: this is a little bit tricky. self here is Aureliano,
                #       but when the call is made the instance of
                #       InternalCommandBase is prepended as usual, so __call__
                #       of InternalCommandBase receives the current self
                #       (Aureliano) as part of *args. That is why _Cmd? gets
                #       the right 'self' and everything works as expected.
                return IntCmd(self, *args)

            return IntCmd
        return command

    #################################
    # Aureliano's internal commands #
    #################################
    @_DefineCommand("Exit.", "Exit", "Bye", "Ciao")
    def __Cmd1(self):
        self._running = False

    @_DefineCommand(("Sleep TIME seconds.", "TIME"), "Wait", "Sleep", "Delay")
    def __Cmd2(self, time):
        try:
            sleep(float(time))
        except ValueError:
            raise BadCommandSyntaxError(self.__name__, args) from None

    @_DefineCommand(("Set a certain mode.", "MODE"), "Be", "Become")
    def __Cmd3(self, state):
        States = {("quiet", "silent"): ("verbose", False),
                  ("verbose", "talkative"): ("verbose", True),
                  ("polite"): ("polite", True),
                  ("impolite"): ("polite", False),
                  ("persistent"): ("continue", True),
                  ("surrendering"): ("continue", False)}

        for knownState in States.keys():
            if state in knownState:
                self.__discipline[States[knownState][0]] = \
                    States[knownState][1]
                break
        else:
            raise BadSyntaxError(repr(state) + " is not a known state!") \
                from None

    @_DefineCommand(("Print help.", "[CMD]"), "Help")
    def __Cmd4(self, Command=None):
        if Command:
            raise NotImplementedError("Command specific help.")
        self.help()


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
        sys.tracebacklimit = 1000
    else:
        sys.tracebacklimit = 0

    if args.cont:
        TheColonel._executePersonalCommand("be persistent")

    if args.polite:
        TheColonel._executePersonalCommand("be polite")

    if args.verbose:
        TheColonel._executePersonalCommand("be verbose")

    if args.run:
        TheColonel.execute(" ".join(args.run))
    elif args.filename:
        TheColonel.interact(args.filename)
    else:
        TheColonel.interact()
