from django.db import models
from django.conf import settings
from django.utils import timezone
import requests, re

class BaseModel(models.Model):

    created = models.DateTimeField(
        auto_now_add=True,
        editable=False
    )

    updated = models.DateTimeField(
        auto_now=True,
        editable=False
    )

    @property
    def admin_change_url(self):
        if self.pk:
            return reverse('admin:%s_%s_change' % (
                self._meta.app_label,
                self._meta.model_name
            ), args=[self.pk])
        return None
    
    @property
    def admin_change_link(self):
        return mark_safe('<span><a href="%s" target="_blank">%s</a></span>' % (self.admin_change_url, self))

    class Meta:
        abstract = True

class Quotation(BaseModel):
	text = models.TextField(max_length=settings.TWITCH_IRC_MAX_LENGTH)
	bucket_name = models.CharField(max_length=100)
	approved = models.BooleanField(default=False)

	@property
	def formatted_text(self):
		formatted = str(self.text)
		formatted = formatted.replace('\r', '').replace('\n', '')
		return str(formatted[0:settings.TWITCH_IRC_MAX_LENGTH])

def default_enabled_buckets():
	buckets = ''
	for bucket in settings.BOT_DEFAULT_BUCKETS:
		buckets += bucket + '\n'
	return buckets

class Channel(BaseModel):
	name = models.CharField(max_length=100)
	bots_enabled = models.BooleanField(default=False)
	bot_minimum_minutes = models.IntegerField(default=settings.BOT_MINIMUM_WAIT_MINUTES)
	bot_maximum_minutes = models.IntegerField(default=settings.BOT_MAXIMUM_WAIT_MINUTES)
	available_to_message_after = models.DateTimeField(auto_now_add=True)
	enabled_buckets = models.TextField(default=default_enabled_buckets())

	def is_bucket_enabled(self, bucket_name):
		return bucket_name in self.enabled_buckets.split()

	@property
	def is_live(self):
		r = requests.get(url=settings.TWITCH_UPTIME_URL+self.name)
		s = str(r.content)
		print(s)
		three_part_time_regex = re.search(r"(\d+)\s+.*,\s+(\d+)\s+.*,\s+(\d+)", s)
		two_part_time_regex = re.search(r"(\d+)\s+.*,\s+(\d+)", s)
		print(three_part_time_regex)
		print(two_part_time_regex)
		if three_part_time_regex is None and two_part_time_regex is None:
			return False
		if three_part_time_regex:
			(hrs, mins, scnds) = three_part_time_regex.groups()
			total_seconds = int(hrs) * 60 * 60 + int(mins) * 60 + int(scnds)
			print (total_seconds)
			return total_seconds > settings.MINIMUM_CHANNEL_UPTIME_SECONDS
		if two_part_time_regex:
			(mins, scnds) = two_part_time_regex.groups()
			total_seconds = int(mins) * 60 + int(scnds)
			print (total_seconds)
			return total_seconds > settings.MINIMUM_CHANNEL_UPTIME_SECONDS

		return False

	def mark_to_run(self):
		self.available_to_message_after = timezone.now()
		self.save()
