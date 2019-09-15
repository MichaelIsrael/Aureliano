from Commands import CommandBase
from collections import OrderedDict

_RE_IP_UNIT = r"([1-9]?[0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])"
_RE_IP = r"\b{0}\.{0}\.{0}\.{0}\b".format(_RE_IP_UNIT)

class CmdTelnet(CommandBase):
    _BriefHelpStr = "Telnet to a system and execute one or several commands."
    __RE_USER_PASS = "[^:]+"
    __RE_System = "(?P<Ip>{IP_RE})\:(?P<Username>{USER_RE})\:(?P<Password>{PASS_RE})".format(IP_RE=_RE_IP, USER_RE=__RE_USER_PASS, PASS_RE=__RE_USER_PASS)

    SingleParametersRegex = OrderedDict([("System","{Ip}(?:\:{User}\:{Pass})?".format(Ip=_RE_IP, User=__RE_USER_PASS, Pass=__RE_USER_PASS))])
    MultiParametersRegex = OrderedDict([("Cmd",".*")]) #TODO


