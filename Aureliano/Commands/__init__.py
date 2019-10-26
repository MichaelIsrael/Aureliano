from Commands.ExternalCommandBase import ExternalCommandBase

from Commands.CmdFtp import CmdFtp
from Commands.CmdTelnet import CmdTelnet
#from Commands.Test.CmdTest import CmdTest
#from Commands.Test.CmdTests import CmdTestchild, CmdTestfree


__add__ = [ExternalCommandBase,
           CmdFtp,
           CmdTelnet,
           #CmdTest, CmdTestchild, CmdTestfree,
           ]
