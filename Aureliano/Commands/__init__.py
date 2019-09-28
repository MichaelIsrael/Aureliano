from Commands.CommandBase import CommandBase

from Commands.CmdFtp import CmdFtp
from Commands.CmdTelnet import CmdTelnet
from Commands.CmdTest import CmdTest


__add__ = [CommandBase,
           CmdFtp,
           CmdTelnet,
           CmdTest,
           ]
