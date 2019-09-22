#!/usr/bin/env python3
from Commands.Exceptions import BadCommandSyntaxError, BadSyntaxError
from ExceptionBase import AurelianoBaseError
from functools import wraps
from time import sleep
from Commands.CommandBase import Helper
from Commands import *
import argparse
import random
import types
import sys
import os
import re

#sys.tracebacklimit = 0

#############
# Constants #
#############
MyName = os.path.splitext(os.path.basename(__file__))[0]
MyVersion = 0.1
MyAuthor = "Michael Israel"


############
# Messages #
############
MsgInteractWelcome = "At your service, sir!"
MsgInteractExit = "Goodbye, sir!"
MsgInsults = ["Are you crazy?", "You must be out of your mind!", "Impossible, sweet cheeks!", "How about we stop messing around and get to work!?", "Don't be ridiculous!", "Think again, Einstein!", "No time for silly jokes, sir!"]


############
# Commands #
############
class Aureliano:
    def __init__(self):
        self.__ComandsFilename = None
        self.__CommandsFileLock = False
        self.__interacting = False
        self.__discipline = {
            "verbose" : True, #TODO: is this even used anywhere? Should be removed or implemented?
            "continue" : False,
            "polite" : False}

        self._internalCommands = {name : self.__class__.__dict__[name] for name in self.__class__.__dict__.keys() if "_Aureliano__Cmd" in name}
        for _, cmdMethod in self._internalCommands.items():
            for CmdName in cmdMethod._CmdNames:
                self.__cloneCommand(CmdName, cmdMethod)


    def __cloneCommand(self, newFunc, origFunc):
        cmdFuncName = "_Cmd"+newFunc.title()
        setattr(self, cmdFuncName, types.FunctionType(origFunc.__code__, origFunc.__globals__, newFunc, origFunc.__defaults__, origFunc.__closure__))
        
    def execute(self, command):
        #TODO: Accept string or iterable.
        try:
            cmd = CommandBase.create(self, command)
        except:
            raise
        else:
            return cmd.run()

    def getHelp(self, command):
        helpList = CommandBase.help()
        try:
            return(helpList[command])
        except:
            return None
        

    def help(self):
        print("{name} {version} at your command!".format(name=MyName, version=MyVersion))

        print(self.getHelpStr())


    def getHelpStr(self):
        # Print internal commands' help
        helpStr = "  Internal commands:"
        for _, intCmd in self._internalCommands.items():
            helpStr += "\n" + re.sub("^", "    ", str(intCmd._CmdHelp), flags=re.MULTILINE)

        helpStr += "\n"

        #Print external commands:
        helpStr += "\n" + "  External commands:"
        for HelpItem in CommandBase.help():
            helpStr += "\n" + "    "+str(HelpItem)

        return helpStr

    def _whisper(self, *args):
        if self.__interacting:
            msg = "Aureliano: " + str(*args)
        else:
            msg = "Aureliano: " + str(*args)
            #raise NotImplementedError #TODO
        return msg

    def _say(self, *args):
        if self.__interacting:
            print(self._whisper(*args))
        else:
            print(self._whisper(*args))
            #raise NotImplementedError #TODO

    def _insult(self):
        if not self.__discipline["polite"]:
            self._say(random.choice(MsgInsults))

    def _handle(self, exception):
        if self.__discipline["continue"] or self.__interacting:
            print(exception)
        else:
            raise exception from None

    def interact(self, Filename=None):
        #TODO: Replace the following with an iterator self for both variants
        self.__readFrom(Filename)
        try:
            for command in self.__readCommandsFile():
                try: self._executePersonalCommand(command)
                except TypeError:
                    try:
                        raise BadCommandSyntaxError(self, command) from None
                    except BadCommandSyntaxError as e:
                        self._handle(e)
                except AttributeError:
                    try:
                        returncode = self.execute(command)
                        if not self.__discipline["continue"] and returncode:
                            break
                    except AurelianoBaseError as e:
                        self._handle(e)
        except TypeError:
            self._say(MsgInteractWelcome)
            self.__interacting = True
            while self.__interacting:
                try:
                    command = self.__getCommand()
                except KeyboardInterrupt:
                    self._say("Couldn't you ask in a nicer way!? How about saying 'bye'!?")
                    self._executePersonalCommand("exit")
                    return

                try: self._executePersonalCommand(command)
                except TypeError:
                    try:
                        raise BadCommandSyntaxError(self, command) from None
                    except BadCommandSyntaxError as e:
                        self._handle(e)
                except AttributeError:
                    try:
                        returncode = self.execute(command)
                        if not self.__discipline["continue"] and returncode != 0:
                            break
                    except AurelianoBaseError as e:
                        self._handle(e)
            self._say(MsgInteractExit)

    def __readFrom(self, Filename):
        assert not self.__CommandsFileLock, "Another commands' file is currently being processed!"
        self.__ComandsFilename = Filename

    def _executePersonalCommand(self, command):
        # Multi-line commands would raise an AttributeError, same as if
        # the command does not exist.
        command = command.split()
        cmdMethodName = "_Cmd"+command[0].title()
        cmdMethod = getattr(self, cmdMethodName)
        return cmdMethod(self, *command[1:])

    class __CInternalAnalysis:
        final = True
        completeCommand = []
        multiComment = False

    __InternalAnalysis = __CInternalAnalysis()
        
    def __analyzeCommand(self, command):
        command = command.strip()

        if self.__InternalAnalysis.multiComment:
            if command == "#>":
                self.__InternalAnalysis.multiComment = False
            return None
        else:
            if command == "#<":
                self.__InternalAnalysis.multiComment = True
                return None

        command = re.sub("#.*$", "", command)

        if command == "":
            return None

        self.__InternalAnalysis.completeCommand.append(command)

        # Check if multiline.
        if command.endswith("{"):
            if not self.__InternalAnalysis.final:
                raise BadSyntaxError(self, "Nested commands are not yet supported!") from None
            self.__InternalAnalysis.final = False
            return None
        elif command == "}":
            if self.__InternalAnalysis.final:
                raise BadSyntaxError(self, "End of unstarted multi-line command!") from None
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

    def __getCommand(self):
        command = input("You: ")
        cmd = self.__analyzeCommand(command)
        if cmd is None:
            return self.__getCommand()
        else:
            return cmd

    def __readCommandsFile(self):
        commandsFile = open(self.__ComandsFilename, 'r')
        self.__CommandsFileLock = True
        finalCommand = None
        for command in commandsFile:
            cmd = self.__analyzeCommand(command)
            if cmd is None:
                continue
            else:
                yield cmd
        #TODO: Check if a multi-line command was not correctly ended.
        commandsFile.close()
        self.__CommandsFileLock = False
        self.__ComandsFilename = None

    ###################################
    # Decorator for defining commands #
    ###################################
    def _DefineCommand(helpStr, *names):
        def command(_Cmd):
            setattr(_Cmd, "_CmdHelp", Helper(names, helpStr))
            setattr(_Cmd, "_CmdNames", names)
            @wraps(_Cmd)
            def commandWrapper(self, *args):
                return _Cmd(self, *args)
            return commandWrapper
        return command

    #################################
    # Aureliano's internal commands #
    #################################
    @_DefineCommand("Exit.", "Exit", "Bye", "Ciao")
    def __Cmd1(self):
        self.__interacting = False

    @_DefineCommand(("Sleep TIME seconds.", "TIME"), "Wait", "Sleep", "Delay")
    def __Cmd2(self, time):
        try:
            sleep(float(time))
        except ValueError:
            raise BadCommandSyntaxError(self, self.__name__, args) from None

    @_DefineCommand(("Set a certain mode.", "MODE"), "Be", "Become")
    def __Cmd3(self, state):
        States = {("quiet","silent"):       ("verbose", False),
                  ("verbose", "talkative"): ("verbose", True),
                  ("polite"):               ("polite", True),
                  ("impolite"):             ("polite", False),
                  ("persistent"):           ("continue", True),
                  ("surrendering"):         ("continue", False)}

        for knownState in States.keys():
            if state in knownState:
                self.__discipline[States[knownState][0]] = States[knownState][1]
                break
        else:
            raise BadSyntaxError(self, repr(state)+" is not a known state!") from None

    @_DefineCommand(("Print help.", "[CMD]"), "Help")
    def __Cmd4(self, Command=None):
        if Command:
            raise NotImplementedError("Command specific help.")
        self.help()
            

if __name__=="__main__":
    TheColonel = Aureliano()

    parser = argparse.ArgumentParser(prog=MyName, formatter_class=argparse.RawDescriptionHelpFormatter, epilog=TheColonel.getHelpStr())
    #-v
    parser.add_argument("-v", "--verbose", help="increase output verbosity.", action="store_true")
    #-p
    parser.add_argument("-p", "--polite", help="No foul language.", action="store_true")
    #-c
    parser.add_argument("-c", "--continue", help="keep going if an error occurs.", action="store_true", dest="cont")

    group = parser.add_mutually_exclusive_group()
    #-r
    group.add_argument("-r", "--run", help="Run one command.", nargs='+', metavar="CMD")
    # Commands file.
    group.add_argument("-f", "--filename", help="Name of a text file containing Aureliano commands to be executed.")

    args = parser.parse_args()

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
