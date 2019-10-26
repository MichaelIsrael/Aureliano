from Commands import ExternalCommandBase
from Commands.Exceptions import BadCommandSyntaxError


class AbstractTest(ExternalCommandBase):
    def _say(self, Msg):
        print("AbsTest {Name}: {Msg}".format(Name=self.Args["Name"], Msg=Msg))


class CmdTestchild(AbstractTest):
    def getDescription(self):
        return "Same as CmdTest but with a parent abstract class"

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
                    raise BadCommandSyntaxError(self, "Wrong syntax!")


class CmdTestfree(AbstractTest):
    def getDescription(self):
        return "Test free mode."

    def registerParameters(self):
        self.addMainParameter("Name", r"\S+")

        print("CmdTestfree IS NOT YET IMPLEMENTED!!")

    def run(self):
        self._say(self.Args)

        raise NotImplementedError
