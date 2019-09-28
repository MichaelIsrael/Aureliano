from Commands import ExternalCommandBase
from collections import OrderedDict
import telnetlib
import getpass


_RE_IP_UNIT = r"([1-9]?[0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])"
_RE_IP = r"\b{0}\.{0}\.{0}\.{0}\b".format(_RE_IP_UNIT)
_RE_USERNAME = r"[^:]+"
_RE_PASSWORD = r"[^:]*"
_RE_System = r"(?P<Ip>{IP_RE})(?:\:(?P<Username>{USER_RE})(?:\:(?P<Password>{PASS_RE}))?)?".format(IP_RE=_RE_IP, USER_RE=_RE_USERNAME, PASS_RE=_RE_PASSWORD)


class CmdTelnet(ExternalCommandBase):
    _BriefHelpStr = "Telnet to a system and execute one or several commands."

    SingleParametersRegex = OrderedDict([("System", r"{Ip}(?:\:{User}(?:\:{Pass})?)?".format(Ip=_RE_IP, User=_RE_USERNAME, Pass=_RE_PASSWORD))])
    MultiParametersRegex = OrderedDict([("Cmd", r".*")])  # TODO

    def run(self):
        try:
            System = re.match(self._RE_System,
                              self.Args["System"]).groupdict()
        except AttributeError:
            raise BadSyntaxError("TODO") from None

        password = System["Password"]
        if password is None:
            password = getpass.getpass()

        _TNSession = telnetlib.Telnet(System["Ip"])

        _TNSession.read_until(b"login: ")
        _TNSession.read_until(b"login: ")

        _TNSession.write(System["Username"].encode('ascii') + b"\n")

        if password:
            _TNSession.read_until(b"Password: ")
            _TNSession.write(password.encode('ascii') + b"\n")

        _TNSession.write(b"ls\n")
        _TNSession.write(b"exit\n")

        print(_TNSession.read_all().decode('ascii'))
