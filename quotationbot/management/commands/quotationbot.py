from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from quotationbot.models import Quotation, Channel
from django.utils import timezone
import socket, re, json, argparse, emoji, csv, random, time, sys

class Command(BaseCommand):
    help = 'Runs the chatbot server'
    verbose_on = False
    __CURRENT_CHANNEL = None

    def connect(self, username = settings.TWITCH_HANDLE, password = settings.TWITCH_OAUTH_TOKEN):
        self.__NICK = username
        self.__PASS = 'oauth:'+str(password).lstrip('oauth:')
        self.__SOCKET = socket.socket()
        self.__SOCKET.connect((settings.TWITCH_IRC_ADDRESS, settings.TWITCH_IRC_PORT))
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


    def add_arguments(self, parser):
        parser.add_argument('bucket_names', nargs='*', type=str)
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='print debug info to the console',
        )
        parser.add_argument(
            '--ignore',
            action='store_true',
            help='server should ignore errors log them and continue running',
        )

    def verbose_write(self, outputstring):
        if self.verbose_on:
            self.stdout.write(self.style.NOTICE('%s: %s' % (timezone.now(),outputstring)))

    def send_random_quotation_to_channel(self, channel, bucket_name):
        quotations = Quotation.objects.filter(bucket_name=bucket_name, approved=True)
        count = quotations.count()
        if count:
            q = quotations[random.randrange(0,count)]
            self.connect()
            self.verbose_write('IRC connection established')
            self.send_message(channel.name, q.formatted_text)
            self.verbose_write('Message sent to %s was %s' %(channel.name, q.formatted_text))   
            self.close_connection()
            self.verbose_write('Connection closed')


    def broadcast_available_messages(self, bucket_name):
        channels = Channel.objects.filter(bots_enabled=True,available_to_message_after__lte=timezone.now())
        self.verbose_write('Number of channels to write to %s' % channels.count())
        for channel in channels:
            self.verbose_write('checking channel %s' % channel.name)
            if channel.is_live:
                self.verbose_write('%s came back as live, send a message' % channel.name)
                self.send_random_quotation_to_channel(channel, bucket_name)
                channel.available_to_message_after = timezone.now() + timezone.timedelta(
                    minutes=random.randrange(channel.bot_minimum_minutes, channel.bot_maximum_minutes + 1))
                channel.save()
                self.verbose_write('%s set to run after %s' % (channel.name, channel.available_to_message_after))

    def handle(self, *args, **options):
        self.verbose_on = options['verbose']
        
        self.buckets = settings.BOT_DEFAULT_BUCKETS
        if 'bucket_names' in options and options['bucket_names']:
            self.buckets = options['bucket_names']

        self.stdout.write(self.style.SUCCESS('Started Server'))
        for bucket in self.buckets:
            self.stdout.write(self.style.SUCCESS('Serving bucket: %s' % bucket))

        self.verbose_write('Verbose mode activated')
        self.verbose_write('Twitch handle: %s' % settings.TWITCH_HANDLE)
        self.verbose_write('oauth token: %s' % settings.TWITCH_OAUTH_TOKEN)
        self.stdout.write(self.style.SUCCESS('Quit the server with CONTROL-C.'))

        if settings.BOT_IGNORE_ERRORS or options['ignore']:
            self.verbose_write('Ignore errors on. Server will log exceptions and attempt to continue running')
            try:
                while True:
                    for bucket in self.buckets:
                        try:
                            self.broadcast_available_messages(bucket)
                        except KeyboardInterrupt:
                            raise KeyboardInterrupt
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(str(e)))
                    time.sleep(settings.QUOTATION_TIME_INTERVAL)
            except KeyboardInterrupt:
                self.stdout.write(self.style.SUCCESS('Stopped server. Keyboard interrupt'))
        else:
            try:
                while True:
                    for bucket in self.buckets:
                        self.broadcast_available_messages(bucket)
                    time.sleep(settings.QUOTATION_TIME_INTERVAL)
            except KeyboardInterrupt:
                self.stdout.write(self.style.SUCCESS('Stopped server. Keyboard interrupt'))


        

        