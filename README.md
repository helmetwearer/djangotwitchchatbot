This app needs documentation still. Initial code checkin, will add later.


Install the reqs (probably should set up a virtualenv etc):
    pip install -r requirements.txt

Create a superuser:
    manage.py createsuperuser

Run the web server:
    manage.py runserver

(for production webserver this is a great guide: https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-django-with-postgres-nginx-and-gunicorn)


Go to the admin and login:
    http://127.0.0.1:8000/admin

For each channel you want the bot to monitor, create a channel object

name should be the exact handle of the twitch channel you want to run the bot in

you must check "bots enabled" to actively scan the channel. Useful for quick and immediate takedown.

the bot will send a message at a random interval between the minimum and maximum minutes set.


For each Quotation you will have to specify a bucketname. This allows us to put quotes into different
chat buckets, and run several different types of quotes at once. The setting BOT_DEFAULT_BUCKETS is helpful here.

In order for the quote to be in the random pool the approved flag must be checked. This allows for quick takedown of any poorly sourced quotes that may have entred the system.


To start the chatbot:

    manage.py quotationbot --verbose --ignore
or

    manage.py quotationbot bucketname1 bucketname2 bucketname3 --verbose --ignore

If no bucket names are passed it will use the setting BOT_DEFAULT_BUCKETS

For bot specific configurables check the settings here:
https://github.com/helmetwearer/djangotwitchchatbot/blob/main/helmetbot/settings.py#L116

Highly encouraged to use a local_settings.py file for stuff like:
    TWITCH_HANDLE = 'your_twitch_user_name'
    TWITCH_OAUTH_TOKEN = 'go here to get an oauth token: https://twitchapps.com/tmi/'
