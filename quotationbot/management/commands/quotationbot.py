from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from quotationbot.models import Quotation, Channel, ChatServerSettings
from quotationbot.mixins import IRCMixin
from django.utils import timezone
import re, json, argparse, random, time, sys, requests

class Command(BaseCommand, IRCMixin):
    help = 'Runs the chatbot server'
    verbose_on = False

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

            if channel.is_needy_gf_channel:
                self.verbose_write('Needy gf channel detected')

                results = requests.post(settings.NEEDY_GF_URL, 
                    data={'phone':channel.name, 'message':q.formatted_text})

                if results.status_code == 200:
                    self.verbose_write('Needy GF message sent to %s was %s' %(channel.name, q.formatted_text))
                else:
                    self.verbose_write('HTTP %s %s' % (results.status_code, results.text))
            else:
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
                self.verbose_write('%s came back as live, check if bucket is on' % channel.name)
                if channel.is_bucket_enabled(bucket_name):
                    self.send_random_quotation_to_channel(channel, bucket_name)
                    channel.available_to_message_after = timezone.now() + timezone.timedelta(
                        minutes=random.randrange(channel.bot_minimum_minutes, channel.bot_maximum_minutes + 1))
                    channel.save()
                    self.verbose_write('%s set to run after %s' % (channel.name, channel.available_to_message_after))
                else:
                    self.verbose_write('%s bucket not enabled on %s' % (bucket_name, channel.name))

    def handle_sleep(self):
        settings_obj = ChatServerSettings.load()
        settings_obj.next_run_at = timezone.now() + timezone.timedelta(
            seconds=settings_obj.chat_server_delay_seconds)
        settings_obj.save()
        self.verbose_write('Sleeping for %s seconds to avoid spamming and network overload' % (
                settings_obj.chat_server_delay_seconds))
        time.sleep(settings_obj.chat_server_delay_seconds)


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
                    self.handle_sleep()
            except KeyboardInterrupt:
                self.stdout.write(self.style.SUCCESS('Stopped server. Keyboard interrupt'))
        else:
            try:
                while True:
                    for bucket in self.buckets:
                        self.broadcast_available_messages(bucket)
                    self.handle_sleep()
            except KeyboardInterrupt:
                self.stdout.write(self.style.SUCCESS('Stopped server. Keyboard interrupt'))

       