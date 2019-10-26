

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
        self.Command = Command

    def getFullHelp(self):
        print(self.Command)
        print(self.Command.getHelp())
        return self.Command.getCommandName() + self.Command.getHelp()

    def __str__(self):
        """ get formated help string. """
        return repr(self)

    def __repr__(self):
        """ get formated help string. """
        # Store command name.
        name = self.Command.getCommandName()

        # Store command help.
        description = self.Command.getDescription()

        # Write help string in a new line if needed.
        if len(name) >= 20:
            description = "\n" + (" " * 20) + description
        return "{Name: <20}{Help}".format(Name=name, Help=description)
