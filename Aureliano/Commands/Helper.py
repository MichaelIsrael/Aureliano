

##################
# Helper classes #
##################
class Helper:
    """A generic class to handle help strings.

    Args:
        Commando (CommandBase): Aureliano command.
        Help (str or (str, str)): TODO
    """
    def __init__(self, Commando, Help=None):
        self._info = {}
        try:
            # Try to parse name of command
            # (TODO: Create a function in CommandBase?)
            # self._info["name"] = Commando.__name__[3:]
            self._info["name"] = repr(Commando)
        except AttributeError:  # Internal commands provide a tuple of names.
            try:
                Help, Params = Help
            except ValueError:
                Params = ""
            finally:
                self._info["name"] = "[{}] {}".format("|".join(Commando),
                                                      Params).strip()
                if len(self._info["name"]) >= 20:
                    self._info["help"] = "\n" + (" " * 20) + Help
                else:
                    self._info["help"] = Help
        else:
            try:
                self._info["help"] = Commando.getBriefHelp(Commando)
            except AttributeError:
                self._info["help"] = Help

    def __str__(self):
        return repr(self)

    def __repr__(self):
        if True:
            return "{name: <20}{help}".format(**self._info)
