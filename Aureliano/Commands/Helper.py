

##################
# Helper classes #
##################
class Helper:
    """A generic class to handle help strings.

    Args:
        Command (CommandBase): Aureliano command.
    """
    def __init__(self, Command):
        """ Constructor """
        # Store command data.
        self._info = {}

        # Store command name.
        try:
            # Get name of command from instance.
            self._info["name"] = Command.getCommandName()
        except TypeError:
            # Get name of command from class.
            self._info["name"] = Command.getCommandName(Command)

        # Store command help.
        try:
            # Get help from instance.
            self._info["name"] = Command.getCommandName()
            self._info["help"] = Command.getBriefHelp()
        except TypeError:
            # Get help from class.
            self._info["help"] = Command.getBriefHelp(Command)

        # Write help string in a new line if needed.
        if len(self._info["name"]) >= 20:
            self._info["help"] = "\n" + (" " * 20) + self._info["help"]

    def __str__(self):
        """ get formated help string. """
        return repr(self)

    def __repr__(self):
        """ get formated help string. """
        return "{name: <20}{help}".format(**self._info)
