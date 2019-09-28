from Commands import ExternalCommandBase
from Commands.Exceptions import BadSyntaxError


class CmdTest(ExternalCommandBase):
    _BriefHelpStr = "Test and example command"

    def registerParameters(self):
        self.addMainParameter("Name", r"\S+")

        # Create an ok command.
        self.createExtendedParametersGroup("ok", "Everything is OK.")

        # Create a new ok command that can take extra arguments.
        self.createExtendedParametersGroup("ok2", "Everything is OK with \
            extra arguments.", True)

        # Create an error group.
        ErrorParamGrp = self.createExtendedParametersGroup("error", "Error \
            occuring.")
        # Define types or error supported.
        ErrorParamGrp.addParameter("Type", r"(syntax|message)")

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
                    raise BadSyntaxError("Wrong syntax!")
