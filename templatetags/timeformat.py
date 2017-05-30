from datetime import datetime, timedelta
from django import template
from django.utils.timesince import timesince
register = template.Library()

def timeformat(value):
	now = datetime.now()
	difference = ''
	try:
		difference = now - value
	except:
		pass

	if difference and difference < timedelta(minutes=1):
		return 'just now'
	else:
		return 'il y a %(time)s' % {'time': timesince(value).split(', ')[0]}

register.filter('timeformat',timeformat)


