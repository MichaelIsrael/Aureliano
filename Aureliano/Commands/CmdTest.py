from Commands import CommandBase
from Commands.Exceptions import BadSyntaxError


class CmdTest(CommandBase):
    _BriefHelpStr = "Test and example command"

    def registerParameters(self):
        self.addMainParameter("Name", "\S+")

        OkParamGrp = self.createExtendedParametersGroup("ok", "Everything is OK.")
        Ok2ParamGrp = self.createExtendedParametersGroup("ok2", "Everything is OK with extra arguments.", True)

        ErrorParamGrp = self.createExtendedParametersGroup("error", "Error occuring.")
        ErrorParamGrp.addParameter("Type", "(syntax|message)")


    def _say(self, Msg):
        print("Test {Name}: {Msg}".format(Name=self.Args["Name"], Msg=Msg))


    def run(self):
        for cmd in self.Args["Extended"]:
            action = cmd["Command"]
            if action == "ok":
                self._say("OK!")
            elif action == "ok2":
                self._say("OK2! ({})".format(cmd["Extra"]))
            elif action == "error":
                if cmd["Type"] == "message":
                    self._say("Error!")
                elif cmd["Type"] == "syntax":
                    raise BadSyntaxError(self._Aureliano, "Wrong syntax!")



