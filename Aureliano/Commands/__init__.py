from Commands.ExternalCommandBase import ExternalCommandBase

from Commands.CmdFtp import CmdFtp
from Commands.CmdTelnet import CmdTelnet
# from Commands.CmdTest import CmdTest


__add__ = [ExternalCommandBase,
           CmdFtp,
           CmdTelnet,
           # CmdTest,
           ]
