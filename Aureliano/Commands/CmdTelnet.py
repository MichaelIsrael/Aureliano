from Commands import ExternalCommandBase
import telnetlib
import getpass


_RE_USER_PASS = r"\S+"  # TODO: Check official rules for usernames.
_RE_IP_UNIT = r"\b([1-9]?[0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\b"
_RE_IP = r"{0}\.{0}\.{0}\.{0}".format(_RE_IP_UNIT)
# _RE_URL = "" # TODO
# _RE_ADDRESS = r'({}|{})'.format(_RE_IP, _RE_URL)
_RE_ADDRESS = _RE_IP


class CmdTelnet(ExternalCommandBase):
    def getDescription(self):
        return "Telnet to a system and execute one or several commands."

    def registerParameters(self):
        self.addMainParameter("System",
                              _RE_IP,
                              Help="Address of the target")

        self.addMainParameter("Username",
                              _RE_USER_PASS,
                              Help="Login username",
                              Optional=True)

        self.addMainParameter("Password",
                              _RE_USER_PASS,
                              Help="Login password",
                              Optional=True)

        """
        Command = self.createExtendedParametersGroup(
            "Command",
            Help="Command to be executed on the target system.")
        """

    def run(self):
        password = self.Args["Password"]
        if password is None:
            password = getpass.getpass()

        _TNSession = telnetlib.Telnet(self.Args["System"])

        _TNSession.read_until(b"login: ")
        _TNSession.read_until(b"login: ")

        _TNSession.write(self.Args["Username"].encode('ascii') + b"\n")

        if password:
            _TNSession.read_until(b"Password: ")
            _TNSession.write(password.encode('ascii') + b"\n")

        _TNSession.write(b"ls\n")
        _TNSession.write(b"exit\n")

        print(_TNSession.read_all().decode('ascii'))
