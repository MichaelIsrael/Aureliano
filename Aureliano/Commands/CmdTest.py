from Commands import CommandBase
from collections import OrderedDict

class CmdTest(CommandBase):
    _BriefHelpStr = "Test and example command"

    _RE_ACTION = "(ok|error_(syntax|message))"

    SingleParametersRegex = OrderedDict([("Name", ".*")])
    MultiParametersRegex = OrderedDict([("TestAction",_RE_ACTION)])

    def _say(self, Msg):
        print("Test {Name}: {Msg}".format(Name=self.Args["Name"], Msg=Msg))

    def run(self):
        try:
            for cmd in self.Args["Multi"]:
                action = cmd["TestAction"]
                if action == "ok":
                    self._say("OK!")
                elif action == "error_message":
                    self._say("Error!")
                elif action == "error_syntax":
                    from Commands.Exceptions import BadSyntaxError
                    raise BadSyntaxError(self._Aureliano, "Wrong syntax!")
        except KeyError:
            action = self.Args["TestAction"]
            if action == "ok":
                self._say("OK!")
            elif action == "error_message":
                self._say("Error!")
            elif action == "error_syntax":
                from Commands.Exceptions import BadSyntaxError
                raise BadSyntaxError(self._Aureliano, "Wrong syntax!")

        print("Done!")


