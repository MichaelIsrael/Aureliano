from ExceptionBase import AurelianoBaseError
from Commands.Helper import Helper


##############
# Exceptions #
##############
class UnkownCommandError(AurelianoBaseError):
    def _formatError(self):
        formated_command = " ".join(self.args)
        return "I don't understand what you mean by: '{}'".format(
            formated_command)

    def getNiceName(self):
        return "Unkown command"


class BadSyntaxError(AurelianoBaseError):
    def _formatError(self):
        return "Bad syntax: '{}'".format(" ".join(self.args))

    def getNiceName(self):
        return "Bad syntax"


class BadCommandSyntaxError(BadSyntaxError):
    def __init__(self, *args, **kwargs):
        self._intCmd = list(args)
        self._cmd = self._intCmd.pop(0)
        self._intCmd = " ".join(self._intCmd)
        super(BadCommandSyntaxError, self).__init__(*args, **kwargs)

    def getNiceName(self):
        return "Bad command syntax"

    def _formatError(self):
        # Create command specific Helper instance.
        CmdHelp = Helper(self._cmd)

        # Get full help text.
        CmdHelp = "\n" + CmdHelp.getFullHelp()

        return "{}: '{}'{}".format(self._cmd.getCommandName(),
                                   self._intCmd,
                                   CmdHelp)
