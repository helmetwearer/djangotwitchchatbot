# NEEDY GF EXTENTION USERS:

You must be running on OSX. You need this app:
[Needy GF Server](https://github.com/helmetwearer/needy_gf_server)

download it, and double click the app, when it asks for permissions say yes. That's it. The rest you can configure in this bot.

To add a needy girlfriend channel:

Name should be the phonenumber i.e. 1231231234

Check the "Is needy gf channel" checkbox

Check the "Bots enabled" checkbox as well.

Do yourself a favor and don't make it go faster than 5 minutes. A chain message feature is in the works that will allow burst behavior.

If you want emotes copy/paste them out of the message app into the quotes.

# Dev Note
Working on getting this in a docker

# Twitch Bot Notes
A note about streamer follower settings and how IRC interaction is implemented. You will have to log into twitch, follow some channels, and actually interact with the web GUI (or perhaps mobile chat would suffice haven't tested). I'm not fixing that, and that's not a lack of technology decision it's an intentional barrier. I highly recommend you use a verified account with your mobile number and have 2FA on.

This app needs documentation still. Initial code checkin, will add later.

# Setup Notes

Install the reqs [probably should set up a virtualenv etc](https://docs.python.org/3/library/venv.html):

    pip install -r requirements.txt

Create a superuser:

    ./manage.py createsuperuser

Run the web server:

    ./manage.py runserver

For a production webserver this is a great guide: 

[Unix setup guide](https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-django-with-postgres-nginx-and-gunicorn)

and you should probably include supervisord with that:

[Daemonize stuff](https://www.agiliq.com/blog/2014/05/supervisor-with-django-and-gunicorn/)

Go to the admin and login:

[Localhost admin url](http://127.0.0.1:8000/admin)

For each channel you want the bot to monitor, create a channel object

name should be the exact handle of the twitch channel you want to run the bot in

you must check "bots enabled" to actively scan the channel. Useful for quick and immediate takedown without having to delete.

the bot will send a message at a random interval between the minimum and maximum minutes set.
however if you set the minimum less than the setting QUOTATION_TIME_INTERVAL don't expect it to work. If you don't know how to change the setting, it's
probably best you can't go lower


For each Quotation you will have to specify a bucketname. This allows us to put quotes into different
chat buckets, and run several different types of quotes at once. The setting BOT_DEFAULT_BUCKETS is helpful here.

In order for the quote to be in the random pool the approved flag must be checked. This allows for quick takedown of any poorly sourced quotes that may have entred the system.


To start the chatbot:

    ./manage.py quotationbot --verbose --ignore
    
or

    ./manage.py quotationbot bucketname1 bucketname2 bucketname3 --verbose --ignore

If no bucket names are passed it will use the setting BOT_DEFAULT_BUCKETS

[For bot specific configurables check the settings](https://github.com/helmetwearer/djangotwitchchatbot/blob/main/helmetbot/settings.py#L116)

[Some of the configurables like twitch tokens can be set in the app here](http://127.0.0.1:8000/admin/quotationbot/chatserversettings/1/change/)
Highly encouraged to use a local_settings.py file for stuff like:

    TWITCH_HANDLE = 'your_twitch_user_name'
    TWITCH_OAUTH_TOKEN = 'go here to get an oauth token: https://twitchapps.com/tmi/'
