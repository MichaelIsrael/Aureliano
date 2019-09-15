from Commands import CommandBase
from collections import OrderedDict, namedtuple
from Commands.Exceptions import BadSyntaxError, BadSyntaxError
from ExceptionBase import AurelianoBaseError
import ftplib
import socket
import re
import os


##############
# Exceptions #
##############
class FtpAnonymousOnlyError(AurelianoBaseError):
    pass

class FailedToConnectError(AurelianoBaseError):
    pass


###################
# General Regexes #
###################
_RE_Path = "(?i)(?:.+\:)?[\sa-z0-9\\\/\_\.\-]+" #TODO: Better path regex.
_RE_IP_UNIT = r"([1-9]?[0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])"
_RE_IP = r"\b{0}\.{0}\.{0}\.{0}\b".format(_RE_IP_UNIT)

class CmdFtp(CommandBase):
    _BriefHelpStr = "Upload, download and delete files using FTP."
    __RE_USER_PASS = "[^:]+" #TODO: Check official rules for usernames.
    __RE_System = "(?P<Ip>{IP_RE})(?:\:(?P<Username>{USER_RE})\:(?P<Password>{PASS_RE}))?".format(IP_RE=_RE_IP, USER_RE=__RE_USER_PASS, PASS_RE=__RE_USER_PASS)

    SingleParametersRegex = OrderedDict([("System","{Ip}(?:\:{User}\:{Pass})?".format(Ip=_RE_IP, User=__RE_USER_PASS, Pass=__RE_USER_PASS))])
    MultiParametersRegex = OrderedDict([("Action",_RE_Path)]) #TODO

    def __ftpPut(self, localPutFile, destinationPutFile):
        print("FTP --> Puting "+localPutFile+" to "+destinationPutFile)
        with open(localPutFile,'rb') as binaryFile:
            try:
                self.__FtpSession.storbinary('STOR '+destinationPutFile, binaryFile)
            except ftplib.error_perm as e:
                if int(e.args[0][:3]) != 553:
                    raise
                self.__createDir(os.path.dirname(destinationPutFile))
                self.__FtpSession.storbinary('STOR '+destinationPutFile, binaryFile)

    def __ftpGet(self, remoteGetFile, destinationGetFile):
        print("FTP --> Geting "+remoteGetFile+" to "+destinationGetFile)
        with open(destinationGetFile, 'wb') as binaryFile:
            self.__FtpSession.retrbinary('RETR '+remoteGetFile, binaryFile.write)

    def __ftpDel(self, remoteDelFile):
        print("FTP --> deleting "+remoteDelFile)
        try:
            self.__FtpSession.delete(remoteDelFile)
        except ftplib.error_perm as e:
            print(e)
            #TODO: Make sure it's a file not found and handle it.
            #raise 
        else:
            print("HERE CHECK!?")
            #TODO: Make sure the file was deleted.
        finally:
            #self.__FtpSession.retrlines("LIST {}".format(remoteDelFile))
            #ret = self.__FtpSession.sendcmd("LIST {}".format(remoteDelFile))
            try: self.__FtpSession.size(remoteDelFile)
            except ftplib.error_perm as e:
                #Expected behavior
                pass
            else:
                #raise DeleteFailed
                print("Delete failed!")
            

    __RE_CmdPut = "(?P<localPutFile>{PATH})\s+(?P<destinationPutFile>{PATH})".format(PATH=_RE_Path)
    __RE_CmdGet = "(?P<remoteGetFile>{PATH})\s+(?P<destinationGetFile>{PATH})".format(PATH=_RE_Path)
    __RE_CmdDel = "(?P<remoteDelFile>{PATH})".format(PATH=_RE_Path)

    __ActionType = namedtuple("Action", ("func", "regex"))
    __supportedActions = OrderedDict([("put",__ActionType(__ftpPut, __RE_CmdPut)), ("get",__ActionType(__ftpGet, __RE_CmdGet)), ("delete",__ActionType(__ftpDel, __RE_CmdDel))])

    def __supportedActionsList(actions):
        return ["({})".format(action) for action in actions.keys()]
    def __supportedActionsREList(actions):
        return ["(?({NUM})(?:{RE}))".format(NUM=index+2, RE=actions[key].regex) for index,key in enumerate(actions)]
    __RE_Cmd = "\s*(?P<Action>(?:{Actions}))\s+{ActREs}\s*".format(Actions="|".join(__supportedActionsList(__supportedActions)), ActREs="".join(__supportedActionsREList(__supportedActions)))

    def __ftpExec(self, Action, **kwargs):
        self.__supportedActions[Action].func(self, **kwargs)

    def __createDir(self, dirname):
        try:
            self.__FtpSession.mkd(dirname)
        except ftplib.error_perm as e:
            if int(e.args[0][:3]) != 550:
                raise e from None

            parent = os.path.dirname(dirname)
            if parent == dirname:
                raise e from None

            self.__createDir(parent)
            self.__FtpSession.mkd(dirname)


    def run(self):
        try:
            System = re.match(self.__RE_System, self.Args["System"]).groupdict()
        except AttributeError:
            raise BadSyntaxError(self._Aureliano, "TODO") from None

        try:
            self.__FtpSession = ftplib.FTP(System["Ip"])
        except socket.error as e:
            raise FailedToConnectError(self._Aureliano, "TODO") from None

        try:
            self.__FtpSession.login(user=System["Username"], passwd=System["Password"])
        except ftplib.error_perm:
            raise FtpAnonymousOnlyError(self._Aureliano, "TODO") from None

        try:
            for cmd in self.Args["Multi"]:
                try:
                    ActionParams = re.match(self.__RE_Cmd, cmd["Action"]).groupdict()
                except AttributeError:
                    raise BadSyntaxError(self._Aureliano, cmd["Action"]) from None
                ActionParams = {key:val for (key, val) in ActionParams.items() if val is not None}
                self.__ftpExec(**ActionParams)
        except KeyError:
            try:
                ActionParams = re.match(self.__RE_Cmd, self.Args["Action"]).groupdict()
            except AttributeError:
                raise BadSyntaxError(self._Aureliano, "TODO") from None
            ActionParams = {key:val for (key, val) in ActionParams.items() if val is not None}
            self.__ftpExec(**ActionParams)


