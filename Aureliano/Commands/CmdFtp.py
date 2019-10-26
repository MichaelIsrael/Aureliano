from Commands import ExternalCommandBase
from ExceptionBase import AurelianoBaseError
import ftplib
import socket
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
_RE_PATH = r"(?i)(?:.+\:)?[\sa-z0-9\\\/\_\.\-]+"  # TODO: Better path regex.
_RE_USER_PASS = r"\S+"  # TODO: Check official rules for usernames.
_RE_IP_UNIT = r"\b([1-9]?[0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\b"
_RE_IP = r"{0}\.{0}\.{0}\.{0}".format(_RE_IP_UNIT)
# _RE_URL = "" # TODO
# _RE_ADDRESS = r'({}|{})'.format(_RE_IP, _RE_URL)
_RE_ADDRESS = _RE_IP


###############
# FTP Command #
###############
class CmdFtp(ExternalCommandBase):
    def getDescription(self):
        return "Upload, download and delete files using FTP."

    def __ftpPut(self, LocalFile, DestinationFile):
        print("FTP --> Puting " + LocalFile + " to " + DestinationFile)
        with open(LocalFile, 'rb') as binaryFile:
            try:
                self.__FtpSession.storbinary('STOR ' + DestinationFile,
                                             binaryFile)
            except ftplib.error_perm as e:
                if int(e.args[0][:3]) != 553:
                    raise
                self.__createDir(os.path.dirname(DestinationFile))
                self.__FtpSession.storbinary('STOR ' + DestinationFile,
                                             binaryFile)

    def __ftpGet(self, RemoteFile, DestinationFile):
        print("FTP --> Geting " + RemoteFile + " to " + DestinationFile)
        with open(DestinationFile, 'wb') as binaryFile:
            self.__FtpSession.retrbinary('RETR ' + RemoteFile,
                                         binaryFile.write)

    def __ftpDel(self, RemoteFile):
        print("FTP --> deleting " + RemoteFile)
        try:
            self.__FtpSession.delete(RemoteFile)
        except ftplib.error_perm as e:
            print(e)
            # TODO: Make sure it's a file not found and handle it.
            # raise
        else:
            print("HERE CHECK!?")
            # TODO: Make sure the file was deleted.
        finally:
            # self.__FtpSession.retrlines("LIST {}".format(RemoteFile))
            # ret = self.__FtpSession.sendcmd("LIST {}".format(RemoteFile))
            try:
                self.__FtpSession.size(RemoteFile)
            except ftplib.error_perm:
                # Expected behavior
                pass
            else:
                # raise DeleteFailed
                print("Delete failed!")

    __supportedActions = {"put": __ftpPut,
                          "get": __ftpGet,
                          "delete": __ftpDel,
                          }

    def __ftpExec(self, Command, **kwargs):
        self.__supportedActions[Command](self, **kwargs)

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

    def registerParameters(self):
        self.addMainParameter("System",
                              _RE_ADDRESS,
                              Help="Address of the target")

        self.addMainParameter("Username",
                              _RE_USER_PASS,
                              Help="Login username",
                              Optional=True)

        self.addMainParameter("Password",
                              _RE_USER_PASS,
                              Help="Login password",
                              Optional=True)

        PutCommand = self.createExtendedParametersGroup(
            "put",
            Help="Put a file on the target system.")
        PutCommand.addParameter("LocalFile",
                                _RE_PATH,
                                Help="Local file to upload.")
        PutCommand.addParameter("DestinationFile",
                                _RE_PATH,
                                Help="Destination file.")

        GetCommand = self.createExtendedParametersGroup(
            "get",
            Help="Download a file from the target system.")
        GetCommand.addParameter("RemoteFile",
                                _RE_PATH,
                                Help="The file to download.")
        GetCommand.addParameter("DestinationFile",
                                _RE_PATH,
                                Help="Local destination.")

        DeleteCommand = self.createExtendedParametersGroup(
            "delete",
            Help="Delete a file on the target system.")
        DeleteCommand.addParameter("RemoteFile",
                                   _RE_PATH,
                                   Help="File to delete.")

    def run(self):
        try:
            self.__FtpSession = ftplib.FTP(self.Args["System"])
        except socket.error:
            raise FailedToConnectError("TODO") from None

        # TODO: Read password from command line if only username is provided.
        try:
            self.__FtpSession.login(user=self.Args["Username"],
                                    passwd=self.Args["Password"])
        except ftplib.error_perm:
            raise FtpAnonymousOnlyError("TODO") from None

        for cmd in self.Args["Extended"]:
            ActionParams = {key: val for (key, val) in cmd.items()
                            if val is not None
                            and key != "FullCommand"}
            self.__ftpExec(**ActionParams)
