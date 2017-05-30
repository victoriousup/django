# -*- coding: utf-8 -*-
from django.db import models, IntegrityError, transaction
from django.core.urlresolvers import reverse
from sorl.thumbnail import ImageField	
from django.core.exceptions import ObjectDoesNotExist,ValidationError
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.utils.text import slugify
from redactor.fields import RedactorField
from django.conf import settings
from io import BytesIO
from os.path import basename
from django.db.models import FileField
from django.forms import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinLengthValidator, BaseValidator, MinValueValidator, MaxValueValidator
from datetime import datetime
from hashlib import sha1
from videothumbs.fields import VideoThumbnailField
from django.contrib.sessions.models import Session
from mptt.models import MPTTModel
from mptt.fields import TreeForeignKey
# Django For Mail
from django.template.loader import render_to_string
from django.utils.html  import strip_tags
from django.core.mail import EmailMultiAlternatives 
from django.dispatch import receiver
from tinymce.models import HTMLField
from django_countries.fields import CountryField

from django.db.models.signals import post_save, post_delete
from django.core.cache import cache

#ABUSE_PREFIX = 'DJANGO_BANISH_ABUSE:'
#BANISH_PREFIX = 'DJANGO_BANISH:'
#WHITELIST_PREFIX = 'DJANGO_BANISH_WHITELIST:'

class BadCaravaneError(ValidationError):
    pass

class CustomImageField(models.ImageField):
	def to_python(self, data):
		f = super(CustomImageField, self).to_python(data)
		if f is None:
			return None
		try:
			from PIL import Image
		except ImportError:
			import Image

		if hasattr(data, 'temporary_file_path'):
			file = data.temporary_file_path()
		else:
			if hasattr(data, 'read'):
				file = BytesIO(data.read())
			else:
				file = BytesIO(data['content'])
		try:
			im = Image.open(file)
			if im.format not in ('PNG', 'JPEG'):
				raise ValidationError(_('allowed extensions'))
		except ImportError:
			raise
		except Exception:
			raise ValidationError(_('allowed extensions'))
		if hasattr(f, 'seek') and callable(f.seek):
			f.seek(0)
		return f


class ContentTypeRestrictedFileField(FileField):
	def __init__(self, *args, **kwargs):
		try:
			self.content_types = kwargs.pop("content_types")
		except:
			pass
		super(ContentTypeRestrictedFileField, self).__init__(*args, **kwargs)

	def clean(self, *args, **kwargs):
		data = super(ContentTypeRestrictedFileField, self).clean(*args, **kwargs)
		file = data.file
		if hasattr(file,"content_type"):
			content_type = file.content_type
			if content_type in self.content_types:
				pass
			else:
				raise forms.ValidationError(_('Type de fichier non pris en charge.'))
		return data

class ModelManager(models.Manager):
	def get_or_none(self, **kwargs):
		try:
			return self.get(**kwargs)
		except ObjectDoesNotExist:
			return None

class Siteinfo(models.Model):
	objects = ModelManager()
	name= models.CharField(max_length=500)
	logo = models.ImageField(max_length=500,upload_to='siteinfo')
	meta_key = models.CharField(max_length=500, null=True, blank=True, default='')
	meta_description = models.TextField(max_length=500, null=True, blank=True, default='')
	meta_author = models.CharField(max_length=256, null=True, blank=True, default='')
	notify_email = models.CharField(max_length=500)
	fb = models.CharField(max_length=500)
	instagram = models.CharField(max_length=500)
	twitter = models.CharField(max_length=500)
	youtube = models.CharField(max_length=500)
	pdf_payment = ContentTypeRestrictedFileField(max_length=200, upload_to='payment',content_types=['application/pdf'])
	accessoires_home_text = models.CharField(max_length=250,null=True,blank=True,default='')
	destock_home_test = models.CharField(max_length=250,null=True,blank=True,default='')
	def __unicode__(self):
		return self.name

class Slider(models.Model):
	objects = ModelManager()
	image= models.ImageField(max_length=200, upload_to='slider')
	position = models.CharField(max_length=200,blank=True)
	content = models.TextField(max_length=200,blank=True)
	status = models.BooleanField(default=True)
	def __unicode__(self):
		return self.content

class Menu(models.Model):
	objects = ModelManager()
	name=models.CharField(max_length=500)
	slug=models.CharField(max_length =200, unique=True)
	status = models.BooleanField(default=False)
	def __unicode__(self):
		return self.name

class Page(models.Model):
	title = models.CharField(max_length=500, null=True, blank=True, default='')
	meta_key = models.CharField(max_length=500, null=True, blank=True, default='')
	meta_description = models.TextField(max_length=500, null=True, blank=True, default='')
	content = RedactorField(null=True, blank=True, default='')
	def __unicode__(self):
		return self.title

class MenuItem(models.Model):
	objects = ModelManager()
	menu = models.ForeignKey(Menu)
	page = models.ForeignKey(Page)
	name = models.CharField(max_length=256, null=True, blank=False, default='')
	link = models.URLField(max_length=256, null=True, blank=True, default='')
	slug = models.SlugField(max_length=255, null=True, unique=True, default='')

class Menu_item(models.Model):
	objects = ModelManager()
	SHOP='Shop'
	CAMP='Camp'
	RENCOTRE='Rencontre'
	DOCUMENTATION='Documentation'
	ANNONCES='Annonces'
	STATIC='Static'
	LINK='Link'
	SELF='_self'
	BLANK='_blank'
	TYPES = ((SHOP,'Shop'),(CAMP,'Camp'),(RENCOTRE,'Rencontre'),(DOCUMENTATION,'Documentation'),(ANNONCES,'Annonces'),(STATIC,'Static'),(LINK,'Link'))
	TARGET = ((SELF,'_self'),(BLANK,'_blank'))
	name=models.CharField(max_length=500)
	menu_type=models.CharField(max_length=200,choices=TYPES,default=SHOP)
	position=models.CharField(max_length=500)
	menu = models.ForeignKey(Menu,related_name='items')
	status = models.BooleanField(default=False)
	target=models.CharField(max_length=200,choices=TARGET,default=SELF)
	def __unicode__(self):
		return self.name

class ContactUs(models.Model):
	first_name = models.CharField(max_length=126, null=True, blank=True, default='')
	last_name = models.CharField(max_length=126, null=True, blank=True, default='')
	email = models.EmailField(max_length=126, null=True, blank=True, default='')
	message = models.CharField(max_length=900, null=True, blank=True, default='')
	created_at = models.DateTimeField(auto_now_add=True)
	def __unicode__(self):
		return self.first_name

class Advertisement(models.Model):
	objects = ModelManager()
	POSITION = (
				('home_right','home_right'),
				('home_bottom','home_bottom'),
				('document_top', 'document_top'),
				('video_top', 'video_top'),
				('forum_top', 'forum_top'),
				('caravane_list_top', 'caravane_list_top'),
				('caravane_list_detail', 'caravane_list_detail'),
				('sites_top', 'sites_top'),
				('geolocation_top', 'geolocation_top'),
				('meetings_detail_top', 'meetings_detail_top'),
				('meetings_archived_top', 'meetings_archived_top'),
				('partners_list_top', 'partners_list_top'),
				('classifieds_list_top', 'classifieds_list_top'),
				('classifieds_detail_top', 'classifieds_detail_top'),
				('destock_list_top', 'destock_list_top'),
				('destock_detail_top', 'destock_detail_top'),
				('meetings_archived_detail_top', 'meetings_archived_detail_top'),
				('products_list_top', 'products_list_top'),
				('products_detail_top', 'products_detail_top')
			)
	name=models.CharField(max_length=500)
	image= models.ImageField(max_length=200, upload_to='content', blank=True)
	width=models.IntegerField(max_length=50,default=0,blank=True)
	height=models.IntegerField(max_length=50,blank=True,default=0)
	position=models.CharField(max_length=200,choices=POSITION,unique=True)
	content = models.TextField(max_length=700,blank=True,verbose_name='Iframe')
	status = models.BooleanField(default=False)
	def __unicode__(self):
		return self.name

class Document(models.Model):

	objects = ModelManager()
	name=models.CharField(max_length=150,blank=False)
	description = models.CharField(max_length=300,blank=True,verbose_name='description')
	slug=models.SlugField(max_length =200,unique=True,blank=True)
	status = models.BooleanField(default=False)

	def __unicode__(self):
		return self.name

	def for_description(self):
		return self.description	

	def for_slug(self):
		return self.slug

	def save(self, force_insert=False, force_update=False, using=None):
		self.slug = slugify(unicode(self.name))
		try:
			super(Document, self).save(commit=False)
		except Exception, e:
			try: 
				doc = Document.objects.latest('id')
				self.slug = "%s-%d" % (slugify(unicode(self.name)),doc.id + 1)
			except Exception, e:
				self.slug = "%s" % (slugify(unicode(self.name)))
		super(Document, self).save()
		
	def get_absolute_url(self):
		return reverse('documents',kwargs={'slug':self.slug})
			
class DocumentItem(models.Model):
	objects = ModelManager()
	LANGUAGE = (
				(u"Français",u"Français"),
				('Anglais','Anglais'),
				('Allemand','Allemand'),
				('Espagnol','Espagnol'),
				('Italien','Italien'),
				('Autres','Autres')
			)
	title=models.CharField(max_length=500)
	description = models.TextField(max_length=700,blank=True)
	pages=models.IntegerField(max_length=200)
	language=models.CharField(max_length=500,choices=LANGUAGE)
	photo= CustomImageField(max_length=200, upload_to='document')
	pdf= ContentTypeRestrictedFileField(max_length=200, upload_to='document',content_types=['application/pdf'])
	pdf= models.FileField(max_length=200, upload_to='document')

	user=models.ForeignKey(User,related_name='documents')
	document=models.ForeignKey(Document,related_name='items')
	status = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return self.title
	def for_description(self):
		return self.description

	def for_pages(self):
		return self.pages

	def for_language(self):
		return self.language

	def for_photo(self):
		return self.photo

	def for_pdf(self):
		return self.pdf

	def get_absolute_url(self):
		return reverse('documents')

	class Meta:
		ordering = ["-id"]

class ChoiceKey(models.Model):
	objects = ModelManager()
	choice_key = models.CharField(max_length=55, null=True, blank=False, unique=True)
	def __unicode__(self):
		return self.choice_key

class ChoiceOption(models.Model):
	objects = ModelManager()
	choice_key = models.ForeignKey(ChoiceKey, related_name='choices')
	choice_options = models.CharField(max_length=512, null=True, blank=False)
	def __unicode__(self):
		return self.choice_options 

	class Meta:
		ordering = ["choice_options"]	

class CaravaneImplantation(models.Model):
	objects = ModelManager()
	name=models.CharField(max_length=250,blank=False,null=True)
	image = ContentTypeRestrictedFileField(max_length=200, upload_to='implantations',content_types=['image/jpeg', 'image/png'])
	sort=models.IntegerField(max_length=50,default=0,blank=True)
	status = models.BooleanField(default=False)

	def __unicode__(self):
		return self.name
	class Meta:
		ordering = ["sort"]	

class Caravane(models.Model):
	STATUS = (
		(0, 'Pending'),
		(1, 'Approve'),
	)
	user = models.ForeignKey(User, related_name='user')
	# caravane_name = models.CharField(max_length=512, null=True, blank=False, default='')
	slug=models.SlugField(max_length =200,unique=True,blank=True)

	# General Information
	caravane_type = models.ForeignKey(ChoiceOption, null=True, blank=False, default='', related_name='caravane_type')
	brand = models.ForeignKey(ChoiceOption, null=True, blank=False, default='', related_name='brand')
	model = models.CharField(max_length=80, null=True, blank=False, default='')
	manufacture_year = models.ForeignKey(ChoiceOption, null=True, blank=False, default='', related_name='manufacture_year')
	country_registration = models.ForeignKey(ChoiceOption, null=True, blank=False, default='', related_name='country_registration')
	number_of_seats = models.ForeignKey(ChoiceOption, null=True, blank=False, default='', related_name='number_of_seats')

	# Weight
	weight =models.CharField(max_length=200,null=True, blank=True, default='')
	total_weight = models.FloatField(null=True, blank=False, default=0 ,validators=[MinValueValidator(100), MaxValueValidator(10000)])
	curb_weight = models.CharField(max_length=200,null=True, blank=True, default='')
	payload = models.CharField(max_length=200,null=True, blank=True, default='')
	weight_in_working_order = models.CharField(max_length=200,null=True, blank=True, default='')
	other_payload1 = models.CharField(max_length=200,null=True, blank=True, default='')
	other_payload2 = models.CharField(max_length=200,null=True, blank=True, default='')
	other_payload3 = models.CharField(max_length=200,null=True, blank=True, default='')
	other_payload4 = models.CharField(max_length=200,null=True, blank=True, default='')

	# Extra Dimension
	external_dimension = models.CharField(max_length=200,null=True, blank=True,default='')
	boom_length = models.CharField(max_length=200,null=True, blank=True,default='')
	external_length_of_box = models.CharField(max_length=200, null=True, blank=True, default='')
	external_width_of_box = models.CharField(max_length=200, null=True, blank=True, default='')
	external_height_of_caravane = models.CharField(max_length=200, null=True, blank=True, default='')
	external_height_of_folded_catavane = models.CharField(max_length=200, null=True, blank=True, default='')
	external_developed_awning = models.CharField(max_length=200, null=True, blank=True, default='')

	# Internal Dimension
	#internal_dimension = models.CharField(null=True, blank=True, default='')
	internal_length_of_box = models.CharField(max_length=200, null=True, blank=True, default='')
	internal_width_of_box = models.CharField(max_length=200, null=True, blank=True, default='')
	#internal_height_of_caravane = models.CharField(max_length=200, null=True, blank=True, default='')
	#internal_height_of_folded_catavane = models.CharField(max_length=200, null=True, blank=True, default='')
	bed_type_size = models.CharField(max_length=80,null=True, blank=True, default='')
	before_caravane_type = models.ForeignKey(ChoiceOption, null=True, blank=True, default='', related_name='before_caravane_type')
	before_caravane_size = models.CharField(max_length=80, null=True, blank=True, default='')
	middle_caravane_type = models.ForeignKey(ChoiceOption, null=True, blank=True, default='', related_name='middle_caravane_type')
	middle_caravane_size = models.CharField(max_length=80, null=True, blank=True, default='')
	back_caravane_type = models.ForeignKey(ChoiceOption, null=True, blank=True, default='', related_name='back_caravane_type')
	back_caravane_size = models.CharField(max_length=80, null=True, blank=True, default='')

	# Autonomy
	drinking_water_tank = models.ForeignKey(ChoiceOption, null=True, blank=True, default='', related_name='drinking_water_tank')
	drinking_water_capacity = models.CharField(max_length=200, null=True, blank=True, default='')
	waste_water_tank = models.ForeignKey(ChoiceOption, null=True, blank=True, default='', related_name='waste_water_tank')
	waste_water_capacity = models.CharField(max_length=200, null=True, blank=True, default='')
	battery = models.ForeignKey(ChoiceOption, null=True, blank=True, default='', related_name='battery')
	battery_power = models.CharField(max_length=200, null=True, blank=True, default='')
	solar_panel = models.ForeignKey(ChoiceOption, null=True, blank=True, default='', related_name='solar_panel')
	solar_power = models.CharField(max_length=200, null=True, blank=True, default='')
	chemical_toiler = models.ForeignKey(ChoiceOption, null=True, blank=True, default='', related_name='chemical_toiler')
	chemical_type = models.ForeignKey(ChoiceOption, null=True, blank=True, default='', related_name='chemical_type')
	refrigerator = models.ForeignKey(ChoiceOption, null=True, blank=True, default='', related_name='refrigerator')
	# refrigerator_type = models.ForeignKey(ChoiceOption, null=True, blank=True, default='', related_name='refrigerator_type')
	refrigerator_type = models.CharField(max_length=200, null=True, blank=True, default='',validators=[MinValueValidator(1), MaxValueValidator(1000)])
	stove = models.ForeignKey(ChoiceOption, null=True, blank=True, default='', related_name='stove')

	stove_type = models.ForeignKey(ChoiceOption, null=True, blank=True, default='', related_name='stove_type')
	heating = models.ForeignKey(ChoiceOption, null=True, blank=True, default='', related_name='heating')
	heating_type = models.ForeignKey(ChoiceOption, null=True, blank=True, default='', related_name='heating_type')
	water = models.ForeignKey(ChoiceOption, null=True, blank=True, default='', related_name='water')
	# water_type = models.ForeignKey(ChoiceOption, null=True, blank=True, default='', related_name='water_type')
	water_type = models.CharField(max_length=200, null=True, blank=True, default='',validators=[MinValueValidator(1), MaxValueValidator(1000)])
	oven = models.ForeignKey(ChoiceOption, null=True, blank=True, default='', related_name='oven')

	# Structur of caracan
	implantation_caravane = models.ForeignKey(CaravaneImplantation, null=True, blank=True, default='',related_name='implant')

	#structure_of_caravane = models.CharField(max_length=80, null=True, blank=True, default='')
	structure_dimention = models.CharField(max_length=80, null=True, blank=True, default='')
	type_of_chassis = models.ForeignKey(ChoiceOption, null=True, blank=True, default='', related_name='type_of_chassis')
	shocks = models.ForeignKey(ChoiceOption, null=True, blank=True, default='', related_name='shocks')
	floor_thickness = models.CharField(max_length=200, null=True, blank=True, default='')
	wall_thickness = models.CharField(max_length=200, null=True, blank=True, default='')
	roof_thickness = models.CharField(max_length=200, null=True, blank=True, default='')
	insulation_type = models.CharField(max_length=80, null=True, blank=True, default='')
	cover = models.CharField(max_length=80, null=True, blank=True, default='')

	# Value
	new_purchased_value = models.CharField(max_length=200, null=True, blank=True, default='')
	current_value = models.CharField(max_length=200, null=True, blank=True, default='')
	link_our_classified = models.CharField(max_length=200, null=True, blank=True, default='')
	list_of_members = models.CharField(max_length=200, null=True, blank=True, default='')
	forum_post = models.CharField(max_length=200, null=True, blank=True, default='')

	# VideoVideoThumbnailField
	#video = ContentTypeRestrictedFileField(max_length=512, upload_to='videos', content_types=['video/mp4'])
	#video = VideoThumbnailField(upload_to='videos', sizes=((430,422),), auto_crop=False)
	video_url = models.URLField(max_length=250, null=True, blank=True, default='')

	status = models.IntegerField(max_length=9, null=True, blank=False, default=0, choices=STATUS)
	__original_caravane_name = None

	def __init__(self, *args, **kwargs):
		super(Caravane, self).__init__(*args, **kwargs)
		self.__original_caravane_name = self.model

	def save(self, force_insert=False, force_update=False, *args, **kwargs):
		if getattr(self, 'model', True):
			try:
				if not self.slug or self.model != self.__original_caravane_name:
					self.slug = slugify(self.model)
				with transaction.atomic():
					super(Caravane, self).save(*args, **kwargs)
			except IntegrityError:
				token = sha1(datetime.now().isoformat())
				key = token.hexdigest()
				self.slug = "%s-%s" % (slugify(self.model),key)
		with transaction.atomic():
			super(Caravane, self).save(*args, **kwargs)
	
	def __unicode__(self):
		return self.slug

class TemplateUpload(models.Model):
	objects = ModelManager()
	user = models.ForeignKey(User, related_name='templates')
	caravane = models.ForeignKey(Caravane, related_name='caravanes', null=True, blank=True, default='')
	template = ContentTypeRestrictedFileField(max_length=200, upload_to='templates',content_types=['image/jpeg', 'image/png'])

	def filename(self):
		return basename(self.template.url)

class VideoCategory(models.Model):
	objects = ModelManager()
	user = models.ForeignKey(User, related_name='video_category')
	category_name=models.CharField(max_length=150,blank=False)
	description = models.TextField(max_length=300,null=True,)
	slug=models.SlugField(max_length =200,unique=True,blank=True)
	orderby = models.IntegerField(default=0,blank=True)
	status = models.BooleanField(default=True)
	def __unicode__(self):
		return self.category_name
	class Meta:
		ordering = ["orderby"]

	def get_videos(self):
		return self.video.filter(status=True)[0:4]

	def save(self, force_insert=False, force_update=False, using=None):
		self.slug = slugify(unicode(self.category_name))
		try:
			super(VideoCategory, self).save(commit=False)
		except Exception, e:
			try: 
				video_cat = VideoCategory.objects.latest('id')
				self.slug = "%s-%d" % (slugify(unicode(self.category_name)),video_cat.id + 1)
			except Exception, e:
				self.slug = "%s" % (slugify(unicode(self.category_name)))
		super(VideoCategory, self).save()	

	def get_absolute_url(self):
		return reverse('video_view',kwargs={'slug':self.slug})	

class Video(models.Model):
	objects = ModelManager()
	user = models.ForeignKey(User, related_name='video_user')
	video_type = models.ForeignKey(VideoCategory, null=True, blank=False, default='', related_name='video')
	name = models.CharField(max_length=512, null=True, blank=False, default='')
	description = models.TextField(max_length=300,null=True,)
	video_url = models.URLField(max_length=250, null=True, blank=False, default='')
	status = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return self.name
	class Meta:
		ordering = ["-id"]

	def remove(self):
		return '<input type="button" value="Delete" onclick="location.href=\'%s/delete/\'" />'%(self.pk)	
	remove.allow_tags = True
		
	def get_absolute_url(self):
		return reverse('video_list')
			
	@property
	def active(self):
		return self.status==True

class VideoComment(models.Model):
	objects = ModelManager()
	comments = models.TextField(max_length=300,null=True,)
	created_at = models.DateTimeField(auto_now_add=True)
	status = models.BooleanField(default=False)
	user = models.ForeignKey(User, related_name='commented')
	video = models.ForeignKey(Video, related_name='comment')

	def __unicode__(self):
		return self.comments

class Site(models.Model):
	objects = ModelManager()
	STATUS = (
		(0, 'Pending'),
		(1, 'Approve'),
	)
	user = models.ForeignKey(User, related_name='sites')
	site_name = models.CharField(max_length=256, null=True, blank=True, default='')
	site_url = models.URLField(max_length=256, null=True, blank=True, default='')
	description = models.CharField(max_length=300, null=True, blank=True, default='')
	photo = ContentTypeRestrictedFileField(max_length=200, upload_to='site_photos',content_types=['image/jpeg', 'image/png'])
	status = models.IntegerField(max_length=9, null=True, blank=False, default=0, choices=STATUS)
	created_at = models.DateTimeField(auto_now_add=True)

# model for PHPBB
class SessionProfile(models.Model):
	objects = ModelManager()
	session = models.ForeignKey(Session, unique=True)
	user = models.ForeignKey(User, null=True) 

class Country(models.Model):
	objects = ModelManager()
	country = models.CharField(max_length=55, null=True, blank=False, unique=True)
	def __unicode__(self):
		return self.country

class State(models.Model):
	objects = ModelManager()
	country = models.ForeignKey(Country, related_name='states')
	state = models.CharField(max_length=512, null=True, blank=False)
	def __unicode__(self):
		return self.state	

class Meeting(models.Model):
	objects = ModelManager()
	STATUS = (
		(0,'Pending'),
		(1, 'Approve'),
		(2, 'Closed'),
	)
	title = models.CharField(max_length=256, null=True, blank=False, default='')
	#description = models.TextField(max_length=10000, null=True, blank=False, default='')
	description = HTMLField()
	start_date = models.DateTimeField(blank=False, default='')
	end_date =	models.DateTimeField(blank=False, default='')
	location = models.CharField(max_length=256, null=True, blank=False, default='')
	latitude = models.CharField(max_length=256, null=True, blank=False, default='')
	longitude = models.CharField(max_length=256, null=True, blank=False, default='')
	address = models.CharField(max_length=256, null=True, blank=False, default='')
	number_of_place = models.IntegerField(max_length=9, null=True, blank=False, default=0)
	meeting_country = models.CharField(max_length=256, null=True, blank=False, default='')
	meeting_city = models.CharField(max_length=256, null=True, blank=False, default='')
	slug=models.SlugField(max_length =200,unique=True,blank=True)

	meeting_status = models.IntegerField(max_length=9, null=True, blank=False, default=0, choices=STATUS)
	created_at = models.DateTimeField(auto_now_add=True)
	
	def __unicode__(self):
		return self.title

	class Meta:
		ordering = ["-start_date"]

	def get_images(self):
		return self.images.filter(status=True)

	def get_link(self):
		return self.links.filter(status=True)

	def get_user(self):
		return self.meeting.filter(status=True)
	@property	
	def get_list(self,year):
		return self.meeting.filter(start_date__year=year)

	@property
	def is_approverd(self):
		return self.meeting_status==1		

	def save(self, force_insert=False, force_update=False, using=None):
		self.slug = slugify(unicode(self.title))
		try:
			super(Meeting, self).save(commit=False)
		except Exception, e:
			try: 
				meeting = Meeting.objects.latest('id')
				self.slug = "%s-%d" % (slugify(unicode(self.title)),meeting.id + 1)
			except Exception, e:
				self.slug = "%s" % (slugify(unicode(self.title)))
		super(Meeting, self).save()		
	
	def get_absolute_url(self):
		return reverse('meeting_view',kwargs={'slug':self.slug})	

class MeetingImage(models.Model):
	objects = ModelManager()
	meeting = models.ForeignKey(Meeting,related_name='images')
	title = models.CharField(max_length=256, null=True, blank=False, default='')
	#description = models.TextField(max_length=300, null=True, blank=False, default='')
	description = HTMLField()
	image = ContentTypeRestrictedFileField(max_length=200,blank=False, upload_to='meeting',content_types=['image/jpeg', 'image/png'])
	sort=models.IntegerField(max_length=50,default=0,blank=True)
	status = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-id"]

	def __unicode__(self):	
		return self.title

class MeetingLink(models.Model):
	objects = ModelManager()
	meeting = models.ForeignKey(Meeting, related_name='links')
	title = models.CharField(max_length=256, null=True, blank=False, default='')
	link = models.URLField(max_length=256, null=True, blank=False, default='')
	sort=models.IntegerField(max_length=50,default=0,blank=True)
	status = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-id"]
	def __unicode__(self):
		return self.title

class MeetingRegistrationForm(models.Model):
	objects = ModelManager()
	meeting = models.ForeignKey(Meeting, related_name='meeting')
	user=models.ForeignKey(User,related_name='register')
	way_to_come = models.ForeignKey(ChoiceOption,related_name='way_to')
	username = models.CharField(max_length=256, null=True, blank=True, default='')
	number_of_adult = models.ForeignKey(ChoiceOption,related_name='adult_count',null=True, blank=False)
	number_of_child = models.ForeignKey(ChoiceOption,related_name='child_count',null=True, blank=False)
	number_of_animals = models.ForeignKey(ChoiceOption,related_name='animal_count',null=True, blank=False)
	name_and_surename = models.TextField(max_length=400,null=True,blank=False,default='')
	name_age_child = models.TextField(max_length=400,null=True,blank=True,default='')
	number_street_name = models.CharField(max_length=400,null=True,blank=False,default='')
	zip_code = models.IntegerField(max_length=255,null=True,blank=False,default='')
	city = models.CharField(max_length=400,null=True,blank=False,default='')
	country = models.ForeignKey(ChoiceOption,related_name='meeting_reg_country')
	cell_number = models.IntegerField(max_length=255,null=True,blank=False,default='')
	email = models.CharField(max_length=400,null=True,blank=False,default='')
	register = models.CharField(max_length=400,null=True,blank=False,default='')
	arrival_date = models.CharField(max_length=400,null=True,blank=False,default='')
	departure_date = models.CharField(max_length=400,null=True,blank=False,default='')
	payment_method = models.ForeignKey(ChoiceOption,related_name='meeting_payment')
	image_option = models.ForeignKey(ChoiceOption,related_name='meeting_img_option')
	image_option_or = models.TextField(max_length=400,null=True,blank=True,default='')
	status = models.BooleanField(default=False)	

	def save(self, force_insert=False, force_update=False, using=None):
		if 	self.status == True:
			subject = 'Réunion a approuvé succès!'
			sender = 'support@lacaravane.com'
			template = 'mail/meeting_submission.html'
			data = {'title':self.meeting.title,'address':self.meeting.address,'start_date':self.meeting.start_date,'end_date':self.meeting.end_date,'description':self.meeting.description}
			to = self.user.email
			html_content = render_to_string(template,{ 'data': data })
			text_content = strip_tags(html_content)
			mail = EmailMultiAlternatives(subject,text_content,sender,[to])
			mail.attach_alternative(html_content,"text/html")
			mail.send()		
		super(MeetingRegistrationForm, self).save()

class ClassifiedCategory(MPTTModel):
	parent = TreeForeignKey(
        'self', null = True, blank = True, default = None,
        related_name = 'children'
    )
	name = models.CharField(max_length=300,null=True,blank=False,default='')
	description = models.TextField(max_length=300,null=True,blank=False,default='')
	slug = models.CharField(max_length=250, null=True,blank=True,default='',unique=True)
	sort = models.IntegerField(max_length=50,null=True,default=0,blank=True)
	status = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	# class MPTTMeta:
	# 	order_insertion_by=['sort']
	class Meta:
		ordering = ["-name"]

	def __unicode__(self):
		return self.name	
	
	def get_classified(self):
		return self.sub_classified.filter(status=True)

	def save(self, force_insert=False, force_update=False, using=None):
		self.slug = slugify(unicode(self.name))
		try:
			super(ClassifiedCategory, self).save(commit=False)
		except Exception, e:
			try: 
				cat = ClassifiedCategory.objects.latest('id')
				self.slug = "%s-%d" % (slugify(unicode(self.name)),cat.id + 1)
			except Exception, e:
				self.slug = "%s" % (slugify(unicode(self.name)))
		super(ClassifiedCategory, self).save()	

	def get_absolute_url(self):
		return reverse('classified_view',kwargs={'slug':self.slug})	

class ClassifiedRegion(models.Model):
	name  = models.CharField(max_length=250,null=True,blank=False,default='')
	slug = models.CharField(max_length=250, null=True,blank=True,default='',unique=True)
	sort = models.IntegerField(max_length=50,null=True,default=0,blank=True)

	def __unicode__(self):
		return self.name

	def save(self, force_insert=False, force_update=False, using=None): 
		self.slug = slugify(unicode(self.name))
		try:
			super(ClassifiedRegion, self).save(commit=False)
		except Exception, e:
			try: 
				cls = ClassifiedRegion.objects.latest('id')
				self.slug = "%s-%d" % (slugify(unicode(self.name)),cls.id + 1)
			except Exception, e:
				self.slug = "%s" % (slugify(unicode(self.name)))
		super(ClassifiedRegion, self).save()

class ClassifiedDepartment(models.Model):
	region = models.ForeignKey(ClassifiedRegion,related_name='classified_dept')
	name  = models.CharField(max_length=250,null=True,blank=False,default='')
	description = models.TextField(max_length=300,null=True,blank=False,default='')
	slug = models.CharField(max_length=250, null=True,blank=True,default='',unique=True)
	sort = models.IntegerField(max_length=50,null=True,default=0,blank=True)
	country = models.CharField(max_length=250,null=True,default=0,blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-id']

	def __unicode__(self):
		return self.name

	def save(self, force_insert=False, force_update=False, using=None): 
		self.slug = slugify(unicode(self.name))
		try:
			super(ClassifiedDepartment, self).save(commit=False)
		except Exception, e:
			try: 
				cls = ClassifiedDepartment.objects.latest('id')
				self.slug = "%s-%d" % (slugify(unicode(self.name)),cls.id + 1)
			except Exception, e:
				self.slug = "%s" % (slugify(unicode(self.name)))
		super(ClassifiedDepartment, self).save()		

class CaravaneBrand(models.Model):
	name = models.CharField(max_length=200,null=True,blank=False,default='')
	status = models.BooleanField(default=False)
	def __unicode__(self):
		return self.name
	class Meta:
		ordering = ['name']	

class CaravaneRegYear(models.Model):
	year = models.IntegerField(max_length=200, null=True, blank=False, default='', validators=[MinValueValidator(1950), MaxValueValidator(2200)])
	status = models.BooleanField(default=False)
	def __unicode__(self):
		return str(self.year)

class Classified(models.Model):
	objects = ModelManager()
	title = models.CharField(max_length=50,null=True,blank=False,default='')
	description = models.TextField(max_length=400,null=True,blank=False,default='')
	user = models.ForeignKey(User,related_name='classified_user',blank=True,default='',null=True)
	category = models.ForeignKey(ClassifiedCategory,related_name='classified',blank=True,default='',null=True)
	sub_category = models.ForeignKey(ClassifiedCategory,related_name='sub_classified',blank=True,default='',null=True)
	department = models.ForeignKey(ClassifiedDepartment,related_name='classified_department',blank=True,default='',null=True)
	brand = models.ForeignKey(CaravaneBrand,related_name='caravane_brand',blank=True,default='',null=True)
	model = models.CharField(max_length=30,null=True,blank=True,default='')
	price = models.IntegerField(max_length=200, null=True, blank=False, default=0, validators=[MinValueValidator(1), MaxValueValidator(1000000)])
	year = models.IntegerField(max_length=200, null=True, blank=True, default=0,validators=[MinValueValidator(1900), MaxValueValidator(2100)])
	phone = models.CharField(max_length=50,null=True,blank=True,default='')
	email = models.CharField(max_length=200,null=True,blank=False,default='')
	location = models.CharField(max_length=250,null=True,blank=True,default='')
	country = CountryField()
	implantation = models.ForeignKey(CaravaneImplantation,blank=True, null=True,related_name='implant_add',default='')
	latitude = models.CharField(max_length=250,null=True,blank=True,default='')
	longitude = models.CharField(max_length=250,null=True,blank=True,default='')
	city = models.CharField(max_length=250,null=True,blank=True,default='')
	status = models.BooleanField(default=False)
	slug = models.CharField(max_length=250, null=True, blank=True, default='', unique=True)
	created_at = models.DateTimeField(auto_now_add=True)
	premium = models.BooleanField(default=False)
	class Meta:	
		ordering = ["-id"]

	def __unicode__(self):
		return self.title
	
	def save(self, force_insert=False, force_update=False, using=None):
		self.slug = slugify(unicode(self.title))
		try:
			super(Classified, self).save(commit=False)
		except Exception, e:
			try: 
				cls = Classified.objects.latest('id')
				self.slug = "%s-%d" % (slugify(unicode(self.title)),cls.id + 1)
			except Exception, e:
				self.slug = "%s" % (slugify(unicode(self.title)))

		if 	self.status == True:
			subject = 'Your classified approved successfully!'
			sender = 'support@lacaravane.com'
			template = 'mail/classified_submission.html'
			data = {'title':self.title,'category':self.category,'department':self.department,'description':self.description}
			to = self.user.email
			html_content = render_to_string(template,{ 'data': data })
			text_content = strip_tags(html_content)
			mail = EmailMultiAlternatives(subject,text_content,sender,[to])
			mail.attach_alternative(html_content,"text/html")
			mail.send()	
		super(Classified, self).save()

	def get_image(self):
		return self.classified_images.filter(status=True)
	def get_absolute_url(self):
		return reverse('view_classified',kwargs={'slug':self.slug})	

class ClassifiedFavorite(models.Model):
	objects = ModelManager()
	classified = models.ForeignKey(Classified,related_name='favorites')
	user = models.ForeignKey(User,related_name='fav_user')
	status = models.BooleanField(default=True)

class ClassifiedImage(models.Model):
	objects = ModelManager()
	classified = models.ForeignKey(Classified,related_name='classified_images',null=True, blank=True, default='')
	image = ContentTypeRestrictedFileField(max_length=200, upload_to='classified',content_types=['image/jpeg', 'image/png'])
	sort = models.IntegerField(max_length=50,null=True,default=0,blank=True)
	status = models.BooleanField(default=True)

	def img_name(self):
		return basename(self.image.url)	
class ClassifiedPriceRange(models.Model):
	objects = ModelManager()
	price_start = models.IntegerField(max_length=50,null=True,default=0,blank=True)
	price_end = models.IntegerField(max_length=50,null=True,default=0,blank=True)
	title = models.CharField(max_length=250,null=True,blank=False,default='')
	def __unicode__(self):
		return self.title

class ClassifiedAbuse(models.Model):
	objects  =  ModelManager()
	classified = models.ForeignKey(Classified,related_name='classified_abuse',null=True, blank=True)
	user = models.ForeignKey(User,related_name='abuse_user')

class MeetingOffer(models.Model):
	objects  =  ModelManager()
	meeting = models.ForeignKey(Meeting,related_name='meeting_offer')
	title = models.CharField(max_length=250,null=True,blank=False,default='')
	image = ContentTypeRestrictedFileField(max_length=200,blank=False, upload_to='meeting_offer',content_types=['image/jpeg', 'image/png','image/gif'])
	description = HTMLField()
	status = models.BooleanField(default=True)

	def __unicode__(self):
		return self.title

class MeetingActivities(models.Model):
	objects  =  ModelManager()
	meeting = models.ForeignKey(Meeting,related_name='meeting_activity')
	title = models.CharField(max_length=250,null=True,blank=False,default='')
	image = ContentTypeRestrictedFileField(max_length=200,blank=False, upload_to='meeting_activity',content_types=['image/jpeg', 'image/png','image/gif'])
	description = HTMLField()
	start_date = models.DateTimeField(blank=False, default='')
	end_date  =	models.DateTimeField(blank=False, default='')
	location = models.CharField(max_length=250,null=True,blank=False,default='')
	latitude = models.CharField(max_length=250,null=True,blank=False,default='')
	longitude = models.CharField(max_length=250,null=True,blank=True,default='')
	activity_city =  models.CharField(max_length=250,null=True,blank=True,default='')
	activity_country = models.CharField(max_length=250,null=True,blank=True,default='')
	status = models.BooleanField(default=True)

	def __unicode__(self):
		return self.title		

class UserCountry(models.Model):
	objects  =  ModelManager()
	country = models.CharField(max_length=250,null=True,blank=False,default='')
	status = models.BooleanField(default=False)
	sort = models.IntegerField(max_length=50,null=True,default=0,blank=False)

	def __unicode__(self):
		return self.country

class UserTownship(models.Model):
	objects  =  ModelManager()
	country = models.ForeignKey(UserCountry,related_name='township')
	township = models.CharField(max_length=250,null=True,blank=False,default='')
	status = models.BooleanField(default=False)
	sort = models.IntegerField(max_length=50,null=True,default=0,blank=False)

	def __unicode__(self):
		return self.township

class UserProfile(models.Model):
	objects  =  ModelManager()
	STATUS = (
		(0,'Classic'),
		(1, 'Caravane dealer'),
		(2, 'Product dealer'),
	)
	user = models.ForeignKey(User,related_name='profile')
	first_name = models.CharField(max_length=250,null=True,blank=True,default='')
	last_name = models.CharField(max_length=250,null=True,blank=True,default='')
	country = models.CharField(max_length=250,null=True,blank=True,default='')
	city = models.CharField(max_length=250,null=True,blank=True,default='')
	country = models.CharField(max_length=250,null=True,blank=True,default='')
	forumpassword = models.CharField(max_length=250,null=True,blank=True,default='')
	location = models.CharField(max_length=250,null=True,blank=True,default='')
	latitude = models.CharField(max_length=250,null=True,blank=True,default='')
	longitude =models.CharField(max_length=250,null=True,blank=True,default='')
	country_short = models.CharField(max_length=250,null=True,blank=True,default='')
	political_short = models.CharField(max_length=250,null=True,blank=True,default='')
	department = models.CharField(max_length=250,null=True,blank=True,default='')
	subscription = models.BooleanField(default=True,blank=True)
	expiry_date = models.DateTimeField(blank=True,null=True)
	user_type = models.IntegerField(max_length=9, null=True, blank=True, default=0, choices=STATUS)
	deactivate = models.BooleanField(default=False,blank=True)
	phplist = models.BooleanField(default=0, blank=True)
	phplist_id = models.IntegerField(max_length=50,null=True,default=0,blank=False)

class ProductCategory(models.Model):
	objects = ModelManager()
	name = models.CharField(max_length=250,null=True,blank=False,default='')
	slug = models.CharField(max_length=250, null=True, blank=True, default='', unique=True)
	sort = models.IntegerField(max_length=50,null=True,default=0,blank=False)
	status = models.BooleanField(default=False)

	def __unicode__(self):
		return self.name

	def save(self, force_insert=False, force_update=False, using=None):
		self.slug = slugify(unicode(self.name))
		try:
			super(ProductCategory, self).save(commit=False)
		except Exception, e:
			try: 
				cat = ProductCategory.objects.latest('id')
				self.slug = "%s-%d" % (slugify(unicode(self.name)),cat.id + 1)
			except Exception, e:
				self.slug = "%s" % (slugify(unicode(self.name)))
		super(ProductCategory, self).save()

	def get_products(self):
		return self.products.filter(status=True)[0:2]

	def complete(self):
		return self.products.filter(status=True,user__profile__subscription=1)[0:2]

	def count(self):
		return self.products.filter(status=True,user__profile__subscription=1)	
			
	def get_absolute_url(self):
		return reverse('product',kwargs={'slug':self.slug})	

class Product(models.Model):
	objects = ModelManager()
	STATUS = (
		(0, 'Unapproved'),
		(1, 'Approved'),
	)
	user = models.ForeignKey(User,related_name='product')
	name = models.CharField(max_length=250,null=True,blank=False,default='')
	category = models.ForeignKey(ProductCategory,related_name='products')
	description = models.TextField(max_length=1000,null=True,blank=False,default='')
	image = ContentTypeRestrictedFileField(max_length=200, upload_to='product',content_types=['image/jpeg', 'image/png','image/jpg',])
	price = models.CharField(max_length=50,null=True,default=0,blank=True)
	shipping_charge = models.CharField(max_length=50,null=True,default=0,blank=True)
	availability = models.DateField(blank=False)
	link = models.URLField(max_length=256, null=True, blank=True, default='')
	#status = models.BooleanField(default=False)
	status = models.IntegerField(max_length=9, null=True, blank=True, default=0, choices=STATUS)
	sort = models.IntegerField(max_length=50,null=True,default=0,blank=True)
	slug = models.CharField(max_length=250, null=True, blank=True, default='', unique=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:	
		ordering = ["-id"]

	def __unicode__(self):
		return self.name

	def save(self, force_insert=False, force_update=False, using=None):
		if self.slug =='':
			self.slug = slugify(unicode(self.name))
			try:
				super(Product, self).save(commit=False)
			except Exception, e:
				try: 
					product = Product.objects.latest('id')
					self.slug = "%s-%d" % (slugify(unicode(self.name)),product.id + 1)
				except Exception, e:
					self.slug = "%s" % (slugify(unicode(self.name)))
		super(Product, self).save()	
	def get_absolute_url(self):
		return reverse('view_product',kwargs={'slug':self.slug})	
			
class Destocking(models.Model): #destock
	objects = ModelManager()
	STATUS = (
		(0, 'Unapproved'),
		(1, 'Approved'),
	)
	user = models.ForeignKey(User,related_name='destock')
	brand = models.ForeignKey(CaravaneBrand,related_name='destock_brand',blank=True,default='',null=True)
	caravane_type = models.ForeignKey(ChoiceOption, null=True, blank=False, default='', related_name='destock_type')
	model = models.CharField(max_length=50,null=True,blank=False,default='')

	weight = models.IntegerField(max_length=200, null=True, blank=False, default='', validators=[MinValueValidator(200), MaxValueValidator(20000)])
	length = models.IntegerField(max_length=200, null=True, blank=False, default='', validators=[MinValueValidator(140), MaxValueValidator(280)])
	inter = models.CharField(max_length=500,null=True,blank=True,default='')
	exter = models.CharField(max_length=500,null=True,blank=True,default='')
	year = models.IntegerField(max_length=200, null=True, blank=True, default='',validators=[MinValueValidator(2000), MaxValueValidator(2050)])
	number_of_place = models.ForeignKey(ChoiceOption, null=True, blank=False, default='', related_name='number_of_place')
	implant_image = ContentTypeRestrictedFileField(max_length=200,null=True, blank=True,upload_to='implant_image',content_types=['image/jpeg', 'image/png'])

	description = models.CharField(max_length=400, null=True, blank=True, default='')
	price = models.IntegerField(max_length=200, null=True, blank=False, default='', validators=[MinValueValidator(1000), MaxValueValidator(200000)])
	phone = models.CharField(max_length=50,null=True,blank=True,default='')
	email = models.CharField(max_length=200,null=True,blank=True,default='')
	location = models.CharField(max_length=250,null=True,blank=True,default='')
	country = CountryField()
	department = models.ForeignKey(ClassifiedDepartment,related_name='destock_department',blank=True,default='',null=True)
	implantation = models.ForeignKey(CaravaneImplantation,blank=True, null=True,related_name='destock_add',default='')
	latitude = models.CharField(max_length=250,null=True,blank=True,default='')
	longitude = models.CharField(max_length=250,null=True,blank=True,default='')
	city = models.CharField(max_length=250,null=True,blank=True,default='')
	status = models.IntegerField(max_length=9, null=True, blank=True, default=0, choices=STATUS)
	slug = models.CharField(max_length=250, null=True, blank=True, default='')
	created_at = models.DateTimeField(auto_now_add=True)
	premium = models.BooleanField(default=True)
	viewcount = models.IntegerField(max_length=200, null=True, blank=True, default='')
	dealername = models.CharField(max_length=250, null=True, blank=True, default='')
	
	def __unicode__(self):
		return self.model

	class Meta:	
		ordering = ["-id"]

	def save(self, force_insert=False, force_update=False, using=None):
		if self.slug =='':
			self.slug = slugify(unicode(self.model))
			try:
				super(Destocking, self).save(commit=False)
			except Exception, e:
				try: 
					destock = Destocking.objects.latest('id')
					self.slug = "%s-%d" % (slugify(unicode(self.model)),destock.id + 1)
				except Exception, e:
					self.slug = "%s" % (slugify(unicode(self.model)))
		super(Destocking, self).save()	

	def get_image(self):
		return self.destocking_images.filter(status=True)

	def get_contact(self):
		return self.contact_destock.filter(status=True)	

	def get_views(self):
		return self.contact_destock.filter(status=False) 	
	def get_absolute_url(self):
		return reverse('destock_details',kwargs={'pk':self.id})
			
class DestockingFavorite(models.Model):
	objects = ModelManager()
	destock = models.ForeignKey(Destocking,related_name='destock_fav')
	user = models.ForeignKey(User,related_name='destock_fav_user')
	status = models.BooleanField(default=True)


class DestockingImage(models.Model):
	objects = ModelManager()
	destocking = models.ForeignKey(Destocking,related_name='destocking_images',null=True, blank=True, default='')
	image = ContentTypeRestrictedFileField(max_length=200, upload_to='destocking',content_types=['image/jpeg', 'image/png'])
	sort = models.IntegerField(max_length=50,null=True,default=0,blank=True)
	status = models.BooleanField(default=True)

	def img_name(self):
		return basename(self.image.url)

class OtherSite(models.Model):
	objects = ModelManager()
	pay_option = (
                (u"Campings en Espagne",u"Campings en Espagne"),
                ('Campings en France','Campings en France')
            )  
	user = models.ForeignKey(User,related_name='othersite_user')
	pay_country = models.CharField(max_length=100,null=True,default='', blank=True, choices=pay_option)
	name = models.CharField(max_length=250,null=True,blank=False,default='')
	description = models.CharField(max_length=400, null=True, blank=True, default='')
	image = ContentTypeRestrictedFileField(max_length=200, upload_to='othersite',content_types=['image/jpeg', 'image/png'])
	links = models.CharField(max_length=256, null=True, blank=True, default='')
	latitude = models.CharField(max_length=256, null=True, blank=True, default='')
	longitude = models.CharField(max_length=256, null=True, blank=True, default='')
	address = models.CharField(max_length=256, null=True, blank=True, default='')
	country = models.CharField(max_length=250,null=True,default=0,blank=True) 
	status = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	
	def __unicode__(self):
		return self.name

class ProductAbuse(models.Model):
	objects = ModelManager()
	user = models.ForeignKey(User,related_name='user_abuse')
	product = models.ForeignKey(Product,related_name='product_abuse')
	status = models.BooleanField(default=True)

class ProductFavorite(models.Model):
	objects = ModelManager()
	user = models.ForeignKey(User,related_name='user_fav')
	product = models.ForeignKey(Product,related_name='product_fav')
	status = models.BooleanField(default=True)	

class Position(models.Model):
	objects = ModelManager()
	position = models.CharField(max_length=250, null=True, blank=True, default='', unique=True)
	def __unicode__(self):
		return self.position	
class BannerImage(models.Model):
	objects = ModelManager()
	position = models.ForeignKey(Position,related_name='banner')
	image = ContentTypeRestrictedFileField(max_length=200, upload_to='content',content_types=['image/jpeg', 'image/png'])
	url = models.URLField(max_length=256, null=True, blank=True, default='')
	code = models.TextField(max_length=5000, null=True, default='', blank=False)
	status = models.BooleanField(default=True)


class Offer(models.Model):
	STATUS = (
		(0, 'boutique'),
		(1, 'caravane'),
	)

	objects = ModelManager()
	price  = models.IntegerField(max_length=50,null=True,default=0,blank=False)
	number_of_caravanes  = models.IntegerField(max_length=50,null=True,default=0,blank=False)
	details = models.CharField(max_length=250, null=True, blank=True, default='', unique=True)
	default = models.BooleanField(default=False)
	status = models.BooleanField(default=False)
	offer_type = models.IntegerField(max_length=9, null=True, blank=False, default=0, choices=STATUS)
	def __unicode__(self):
		return self.details

class Subscription(models.Model):
	objects = ModelManager()
	PayMethod = (
                (u"paiement mensuel par virement bancaire",u"paiement mensuel par virement bancaire"),
                (u"paiement trimestriel par chèque",u"paiement trimestriel par chèque")
            )  
	tit = (
			(u"M.",u"M."),
            ('Mme','Mme'),
            ('Mlle','Mlle')
		)
	offer_product = models.ForeignKey(Offer, related_name='sub_offer_product',blank=True, null=True)
	offer_destock = models.ForeignKey(Offer, related_name='sub_offer_destock',blank=True, null=True)
	purchaser = models.ForeignKey(User,related_name='sub_user')
	company_name = models.CharField(max_length=100, null=True, blank=True, default='')
	manager_name = models.CharField(max_length=100, null=True, blank=True, default='')
	email = models.EmailField(max_length=126, null=True, blank=True, default='')
	contact_number = models.CharField(max_length=100, null=True, blank=True, default='')
	country = CountryField() 
	payment_method = models.CharField(max_length=100,null=True,default='', blank=True, choices=PayMethod)
	title = models.CharField(max_length=100,null=True,default='', blank=True, choices=tit)
	campany_address = models.CharField(max_length=100,null=True,default='',blank=True)
	campany_post = models.CharField(max_length=100,null=True,default='',blank=True)
	campany_state = models.CharField(max_length=100,null=True,default='',blank=True)
	campany_url = models.CharField(max_length=100,null=True,default='',blank=True)
	client_fname = models.CharField(max_length=100,null=True,default='',blank=True)
	client_email = models.EmailField(max_length=100,null=True,default='',blank=True)
	client_phone = models.CharField(max_length=100,null=True,default='',blank=True)

	purchased_at = models.DateTimeField(auto_now_add=True)
	expiry_date = models.DateTimeField(blank=True,null=True)
	status = models.BooleanField(default=True)	
	#loaction
	campany_city = models.CharField(max_length=100,null=True,default='',blank=True)
	campany_latitude = models.CharField(max_length=100,null=True,default='',blank=True)
	campany_longitude = models.CharField(max_length=100,null=True,default='',blank=True)

	def __unicode__(self):
		return self.company_name
	class Meta:	
		ordering = ["-id"]

class Createemailalert(models.Model):
	objects = ModelManager()
	user = models.ForeignKey(User,related_name='alertuser')
	brand = models.ForeignKey(CaravaneBrand,related_name='alert_brand',blank=True,default='',null=True)
	caravane_type = models.ForeignKey(ChoiceOption, null=True, blank=False, default='', related_name='alert_cravane_type')
	implantation = models.ForeignKey(CaravaneImplantation,blank=True, null=True,related_name='alert_imp',default='')
	price  = models.ForeignKey(ClassifiedPriceRange,related_name='alert_price',blank=True,default='',null=True)
	country = CountryField()
	status = models.BooleanField(default=True)

class CaravaneContact(models.Model):
	objects = ModelManager()
	user = models.ForeignKey(User,related_name='contact_user')
	destock = models.ForeignKey(Destocking,related_name='contact_destock')
	status = models.BooleanField(default=True)
	class Meta:	
		ordering = ["-id"]

class Newspaper(models.Model):
	objects = ModelManager()
	title = models.CharField(max_length=250, null=True, default='', blank=False)
	description = models.TextField(max_length=500, null=True, default='', blank=False)
	image = ContentTypeRestrictedFileField(max_length=200, upload_to='newspaper',content_types=['image/jpeg', 'image/png','image/gif'])
	link = models.URLField(max_length=250, null=True, blank=False, default='')
	slug = models.SlugField(max_length=255, null=True, blank=True)
	sort = models.IntegerField(max_length=50,null=True,default=0,blank=True)
	status = models.BooleanField(default=True)

	def save(self, force_insert=False, force_update=False, using=None):
		if self.slug =='':
			self.slug = slugify(unicode(self.title))
			try:
				super(Newspaper, self).save(commit=False)
			except Exception, e:
				try: 
					newspaper = Newspaper.objects.latest('id')
					self.slug = "%s-%d" % (slugify(unicode(self.title)),newspaper.id + 1)
				except Exception, e:
					self.slug = "%s" % (slugify(unicode(self.title)))
		super(Newspaper, self).save()	
	def __unicode__(self):
		return self.title
	class Meta:	
		ordering = ["sort"] 

class History(models.Model):
	objects = ModelManager()
	work = models.TextField(max_length=500, null=True, default='', blank=False)
	number_of_pages = models.IntegerField(max_length=50,null=True,default=0,blank=False)
	event_date = models.DateTimeField(blank=False, default='')
	status = models.BooleanField(default=True)
	def __unicode__(self):
		return self.work
	class Meta:	
		ordering = ["event_date"]	

class Partners(models.Model):
	objects = ModelManager()
	title = models.CharField(max_length=250, null=True, default='', blank=False)		
	image = ContentTypeRestrictedFileField(blank=True,max_length=200, upload_to='partners',content_types=['image/jpeg', 'image/png','image/gif'])
	description = models.TextField(max_length=500, null=True, default='', blank=True)
	status = models.BooleanField(default=True)
	def __unicode__(self):
		return self.title
	class Meta:	
		ordering = ["-id"]	

class StatisticPage(models.Model):
	title = models.CharField(max_length=500, null=True, blank=True, default='')
	content = RedactorField(null=True, blank=True, default='')
	def __unicode__(self):
		return self.title

class Statistic(models.Model):
	objects = ModelManager()
	title = models.CharField(max_length=250, null=True, default='', blank=False)
	page = models.ForeignKey(StatisticPage, related_name='statistic_page',blank=True)
	number_of_visitors = models.IntegerField(max_length=50,null=True,default=0,blank=True)
	number_of_page_views = models.IntegerField(max_length=50,null=True,default=0,blank=True)
	avg_number_of_page_visitors = models.IntegerField(max_length=50,null=True,default=0,blank=True)
	link = models.URLField(max_length=250, null=True, blank=True, default='')
	slug = models.SlugField(max_length=255, null=True, unique=True, default='')
	year = models.IntegerField(max_length=50,null=True,default=0,blank=False)
	month = models.IntegerField(max_length=50,null=True,default=0,blank=False)
	date = models.DateField(blank=False)
	def __unicode__(self):
		return self.title

class Membre(models.Model):
	objects = ModelManager()
	prenom = models.CharField(max_length=30, null=True, default='', blank=False)
	nom = models.CharField(max_length=30, null=True, default='', blank=False)
	email = models.CharField(max_length=50, null=True, default='', blank=False)
	login = models.CharField(max_length=20, null=True, default='', blank=False)
	password = models.CharField(max_length=30, null=True, default='', blank=False)
	actif = models.BooleanField(default=True)
	inscription = models.DateField(blank=False);
	def __unicode__(self):
		return self.nom

class Externalclassified(models.Model):
	objects = ModelManager()
	id_membre = models.IntegerField(max_length=50,null=True,default=0,blank=True)
	id_cat = models.IntegerField(max_length=50,null=True,default=0,blank=True)
	type = models.IntegerField(max_length=50,null=True,default=0,blank=True)
	titre = models.CharField(max_length=50, null=True, default='', blank=False)
	description = models.TextField(max_length=500, null=True, blank=True, default='')
	valide = models.BooleanField(default=True)
	nbr_photos = models.IntegerField(max_length=50,null=True,default=0,blank=True)
	departement = models.IntegerField(max_length=50,null=True,default=0,blank=True)
	actif = models.BooleanField(default=True)
	date = models.DateField(blank=False)		

class Externalcategorie(models.Model):
	objects = ModelManager()
	type = models.IntegerField(max_length=50,null=True,default=0,blank=True)
	nom = models.CharField(max_length=50, null=True, default='', blank=False)
	nbr_annonces = models.IntegerField(max_length=50,null=True,default=0,blank=True)



class Banishment(models.Model):

    # Flush out time constrained banned in future revisions
    # ban_start = models.DateField(help_text="Banish Start Date.")
    # ban_stop = models.DateField(help_text="Banish Stop Date.")
    # ban_is_permanent = models.BooleanField(help_text="Is Ban Permanent? (Start/Stop ignored)")

    ban_reason = models.CharField(max_length=255, help_text="Reason for the ban?")

    BAN_TYPES = (
        ('ip-address', 'IP Address'),
        ('user-agent', 'User Agent'),
    )

    type = models.CharField(
        max_length=20,
        choices=BAN_TYPES,
        default=0,
        help_text="Type of User Ban to store"
    )

    condition = models.CharField(
        max_length=255,
        help_text='Enter an IP to ban/whitelist, or a User Agent string to ban'
    )

    def __unicode__(self):
        return "Banished %s %s " % (self.type, self.condition)

    def __str__(self):
        return self.__unicode__()

    def is_current(self):
        if self.permanent or self.stop > datetime.date.today(): 
            return True
        return False

    class Meta:
        permissions = (("can_ban_user", "Can Ban User"),)
        verbose_name = "Banishment"
        verbose_name_plural = "Banishments"
        db_table = 'banishments'


class Whitelist(models.Model):
    whitelist_reason = models.CharField(max_length=255, help_text="Reason for the whitelist?")

    WHITELIST_TYPES = (
        ('ip-address-whitelist', 'Whitelist IP Address'),
    )

    type = models.CharField(
        max_length=20,
        choices=WHITELIST_TYPES,
        default=0,
        help_text='Enter an IP address to whitelist'
    )

    condition = models.CharField(
        max_length=255,
        help_text='Enter an IP to whitelist'
    )

    def __unicode__(self):
        return "Whitelisted %s %s " % (self.type, self.condition)

    def __str__(self):
        return self.__unicode__()

    class Meta:
        permissions = (("can_whitelist_user", "Can Whitelist User"),)
        verbose_name = "Whitelist"
        verbose_name_plural = "Whitelists"
        db_table = 'whitelists'


def _generate_cache_key(instance):
    if instance.type == 'ip-address-whitelist':
         cache_key = WHITELIST_PREFIX + instance.condition
    if instance.type == 'ip-address':
         cache_key = BANISH_PREFIX + instance.condition
    abuse_key = ABUSE_PREFIX + instance.condition
    return cache_key, abuse_key


def _update_cache(sender, **kwargs):
    # add a whitelist entry and remove any abuse counter for an IP
    instance = kwargs.get('instance')
    cache_key, abuse_key = _generate_cache_key(instance)
    cache.set(cache_key, "1")
    cache.delete(abuse_key)


def _delete_cache(sender, **kwargs):
    instance = kwargs.get('instance')
    cache_key, abuse_key = _generate_cache_key(instance)
    cache.delete(cache_key)


post_save.connect(_update_cache, sender=Whitelist)
post_save.connect(_update_cache, sender=Banishment)
post_delete.connect(_delete_cache, sender=Whitelist)
post_delete.connect(_delete_cache, sender=Banishment)
