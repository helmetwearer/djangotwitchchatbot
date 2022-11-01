from quotationbot.models import ChatServerSettings
import socket

class IRCMixin():
    __CURRENT_CHANNEL = None

    def connect(self, username=None, password=None):
        settings_obj = ChatServerSettings.load()
        if username is None:
            username = settings_obj.twitch_handle
        if password is None:
            password = settings_obj.twitch_oauth_token
        self.__NICK = username
        self.__PASS = 'oauth:'+str(password).lstrip('oauth:')
        self.__SOCKET = socket.socket()
        self.__SOCKET.connect((settings_obj.twitch_irc_address, int(settings_obj.twitch_irc_port)))
        self.__send_raw('CAP REQ :twitch.tv/tags')
        self.__send_raw('PASS ' + self.__PASS)
        self.__send_raw('NICK ' + self.__NICK)
    
    def __send_raw(self, string):
        self.__SOCKET.send((string+'\r\n').encode('utf-8'))

    def __join_channel(self,channel_name):
        channel_lower = channel_name.lower()

        if(self.__CURRENT_CHANNEL != channel_lower):
            self.__send_raw('JOIN #{}'.format(channel_lower))
            self.__CURRENT_CHANNEL = channel_lower

    def close_connection(self):
        self.__SOCKET.close()

    def send_message(self, channel_name, message):
        self.__join_channel(channel_name)
        self.__send_raw('PRIVMSG #{} :{}'.format(channel_name.lower(),message))