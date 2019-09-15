
#############################
# Base class for exceptions #
#############################
class AurelianoBaseError(Exception):
    def __init__(self, Aureliano = None, *args, **kwargs):
        self._Aureliano = Aureliano
        try:
            self._Aureliano._insult()
        except AttributeError:
            pass
        super(AurelianoBaseError, self).__init__(*args, **kwargs)

    def _formatError(self):
        return str(self.args)

    def __str__(self):
        ErrorMessage = self._formatError()
        try:
            return self._Aureliano._whisper(ErrorMessage)
        except AttributeError:
            return ErrorMessage
            
