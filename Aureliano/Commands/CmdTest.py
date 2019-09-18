from Commands import CommandBase

_RE_ACTION = "(ok|error_(syntax|message))"

class CmdTest(CommandBase):
    _BriefHelpStr = "Test and example command"

    def registerParameters(self):
        self.addMainParameter("Name", ".+")
        self.addExtendedParameter("TestAction", _RE_ACTION)

    def _say(self, Msg):
        print("Test {Name}: {Msg}".format(Name=self.Args["Name"], Msg=Msg))

    def run(self):
        MultiArgs = self.Args.pop("Multi")
        for cmd in MultiArgs:
            action = cmd["TestAction"]
            if action == "ok":
                self._say("OK!")
            elif action == "error_message":
                self._say("Error!")
            elif action == "error_syntax":
                from Commands.Exceptions import BadSyntaxError
                raise BadSyntaxError(self._Aureliano, "Wrong syntax!")



