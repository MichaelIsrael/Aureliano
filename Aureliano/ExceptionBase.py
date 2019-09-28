

#############################
# Base class for exceptions #
#############################
class AurelianoBaseError(Exception):
    def __init__(self, *args, **kwargs):
        super(AurelianoBaseError, self).__init__(*args, **kwargs)

    def _formatError(self):
        return str(self.args)

    def __str__(self):
        return self._formatError()
