from ExceptionBase import AurelianoBaseError

##############
# Exceptions #
##############
class UnkownCommandError(AurelianoBaseError):
    def _formatError(self):
        try:
            formated_command = " ".join(self.args)
        except:
            formated_command = " ".join(self.args[0])
        return "I don't understand what you mean by: '{}'".format(formated_command)

class BadSyntaxError(AurelianoBaseError):
    def _formatError(self):
        return "Bad syntax: '{}'".format(" ".join(self.args))

class BadCommandSyntaxError(BadSyntaxError):
    def __init__(self, Aureliano, *args, **kwargs):
        self._intCmd = list(args)
        self._cmd = self._intCmd.pop(0)
        self._intCmd = " ".join(self._intCmd)
        super(BadCommandSyntaxError, self).__init__(Aureliano, *args, **kwargs)

    def _formatError(self):
        try:
            ## TODO: Get syntax help!
            CmdHelp = self._Aureliano.getHelp(self._cmd)
        except AttributeError:
            return "Internal Error: Could not retrieve the help information!"
        else:
            if CmdHelp is None:
                CmdHelp = ""
            else:
                CmdHelp = "\n  " + str(Helper(self._cmd,CmdHelp))
            return "Bad syntax: {}: '{}'{}".format(self._cmd, self._intCmd, CmdHelp)

