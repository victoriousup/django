# -*- coding: utf-8 -*-
import requests
import json
from django import forms
import datetime
import string
from dateutil.relativedelta import relativedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q,Count,Sum
from lacaravane.forms import SignupForm,ResetPasswordForm,DocumentItemForm,DocumentSortForm,CaravaneModelForm,VideoModelForm,CaravaneSearchForm,VideoSortForm,ClassifiedFavForm,DocumentItemDocumentsForm,VideoCommentForm,SiteForm,SortForm,ContactUsForm,MeetingRegForm,ClassifiedModelForm,DestockModelForm,ClassfifiedSearchForm,ClassifiedAbuseForm,ClassfifiedEmailForm,AccountUserFrom,ClassifiedPriceRange,ProductModelForm,ProductModelForm,ProductEmailForm,ProductAbuseForm,DestockSearchForm,DestockFavForm,MysaleForm,CreateemailalertForm,OthersiteModelForm,subscriptionForm,HistorySearchForm

from lacaravane.models import Video,Siteinfo,Slider,Document,DocumentItem,Caravane,Advertisement,TemplateUpload,Site,Page,MenuItem,ChoiceKey,ChoiceOption,VideoCategory,Meeting,MeetingImage,MeetingLink,ClassifiedCategory,ClassifiedDepartment,ClassifiedFavorite,ClassifiedImage,DestockingImage,Classified,CaravaneImplantation,MeetingRegistrationForm,MeetingOffer,UserCountry,UserTownship,UserProfile,ProductCategory,Product,ProductAbuse,BannerImage,Position,Destocking,DestockingFavorite,Offer,Subscription,Createemailalert,ProductFavorite,OtherSite,CaravaneContact,Newspaper,History,Partners,Menu,Statistic, Membre,Externalclassified, Externalcategorie

from lacaravane.app_context import siteinfo
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, Http404, QueryDict, JsonResponse
from allauth.account.views import AjaxCapableProcessFormViewMixin, FormView
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import TemplateView, View
from django.contrib import messages

# For mail template
from django.template.loader import render_to_string
from django.utils.html  import strip_tags
from django.core.mail import EmailMultiAlternatives 
from .filters import CaravaneFilter,ClassifiedFilter,DestockFilter,AlertFilter
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from lacaravane.models import SessionProfile
from django.utils.encoding import smart_str, smart_unicode
from paypal.standard.forms import PayPalPaymentsForm	
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.views.decorators.csrf import csrf_exempt 
from django.core.signals import request_finished
from django.dispatch import Signal
from allauth.account.views import LoginView
from allauth.account.forms import SignupForm
from querybuilder.query import Query
from django.db import connection, transaction
from django.contrib.auth import get_user_model

from django.contrib.auth.decorators import login_required
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django.template import loader
import random

class CustomLoginView(LoginView):
	def get_context_data(self, **kwargs):
		context = super(CustomLoginView,
						self).get_context_data(self, **kwargs)
		context['signup_form'] = SignupForm()
		return context


log_it = Signal(providing_args=['message', 'level'])
def send_html_email(subject,sender,to,template,template_data,file_path = None,img_path=None):
	html_content = render_to_string(template,template_data)
	text_content = strip_tags(html_content)
	mail = EmailMultiAlternatives(subject,text_content,sender,[to])
	mail.attach_alternative(html_content,"text/html")
	if file_path:
		mail.attach_file(file_path)
	if img_path:
		mail.attach_file(img_path)
	mail.send()

def MailtoAlert(**kwargs):
	message, level = kwargs['message'], kwargs['level']
	data = {'implantation':message['implantation'],'caravane_type':message['caravane_type'], 'brand':message['brand'], 'country':message['country'], 'price':message['price'] }	
	destock = Destocking.objects.get_or_none(pk=level)
	if data:
		custom_dict = {}
		for value in data:
			val = data.get(value)
			if val is not '':
				custom_dict[value] = val

		query_dict = QueryDict('')
		query_dict = query_dict.copy()
		query_dict.update(custom_dict)
		users = AlertFilter(query_dict, queryset=Createemailalert.objects.all())	
		if users:
			for user in users:
				mail_id = user.user.email
				subject = 'Nouveau trailer pour répondent à votre demande'
				sender = 'support@lacaravane.com'
				send_html_email(subject,sender,mail_id,'mail/caravane_search.html',{ 'data': destock })


log_it.connect(MailtoAlert)
	

def home(request):
	info=siteinfo
	data = {}
	data['info'] = info
	return render(request, 'base/home.html',data)

def ViewForumPage(request):
	template_name = 'base/forum.html'
	return render(request,template_name)

def ViewForumAuPage(request):
	template_name = 'base/forum_au.html'
	return render(request,template_name)

def ViewForumFrPage(request):
	template_name = 'base/forum_fr.html'
	return render(request,template_name)

def site_custom_view(request):
	return render(request, 'sitemap/sitemap.xml', {"foo": "bar"}, content_type="application/xhtml+xml")


def ViewChatPage(request):
	template_name = 'base/chat.html'
	return render(request,template_name)	

def PaymentCancelled(request):
	template_name = "base/payment_cancelled.html"
	return render(request, template_name, {'errors':""})

def contact_us(request):
	template_name = 'base/contact_us.html'
	form = ContactUsForm
	if request.method == 'POST':
		to = 'webmaster@lacaravane.com'
		form = ContactUsForm(request.POST)
		try:
			siteinfo = Siteinfo.objects.get_or_none()
		except:
			pass
		if siteinfo.notify_email !='':	
			to = siteinfo.notify_email 

		if form.is_valid():
			form.save()
			data = form.cleaned_data
			subject = data['first_name'] + ' would like to contact.'
			sender = data['email']
			send_html_email(subject,sender,to,'mail/contact_us.html',{ 'data': data })
			messages.success(request, "Merci de nous avoir envoyé ce message. Nous y répondrons dans les 48 heures.")
			return redirect('contact_us')
		else:
			messages.warning(request, "Impossible de répondre à votre demande")
	return render(request, template_name, {'form': form})

def password_reset(request):
	form = ResetPasswordForm(request.POST)
	response = {}
	status = 200
	if form.is_valid():
		form.save()
		response['success'] = 'Un email vous a été envoyé pour la réinitialisation de votre mot de passe.';
	else:
		status = 403
		response['errors'] = form.errors
	return HttpResponse(json.dumps(response),
						status=status,
						content_type='application/json')

def custom_paginate(obj, page='', total=''):
	paginator = Paginator(obj, total)
	try:
		lists = paginator.page(page)
	except PageNotAnInteger:
		lists = paginator.page(1)
	except EmptyPage:
		lists = paginator.page(paginator.num_pages)
	return lists

def documents(request, slug=None):
	template_name='base/documents.html'
	if slug is None or slug == 'None':
		items = DocumentItem.objects.filter(status=True)
		form = DocumentItemDocumentsForm()
		document = None
	else:
		document = Document.objects.get(slug=slug, status=True)
		form = DocumentItemForm()
		form.document= document.id
		items = document.items.filter(status=True)
		# if document is None:
		# 	raise Http404

	if request.method=='POST':
		if slug is None or slug == 'None':
			form = DocumentItemDocumentsForm(request.POST,request.FILES)
		else:
			form = DocumentItemForm(request.POST,request.FILES)
			form.document = Document.objects.get_or_none(id=request.POST.get('document'))
		form.user = request.user.id

		if form.is_valid():
			doc_item = form.save(commit=False)
			doc_item.save()
			messages.success(request, "Documents enregistrés !")
			subject='Nouveau document créé'
			sender='support@lacaravane.com'
			to='yoann.ferrand@prediseo.com'
			send_html_email(subject,sender,to,'mail/document.html',{'form':doc_item},doc_item.pdf.path,doc_item.photo.path)
			return redirect('documents') if slug is None or slug == 'None' else redirect('documents', slug=slug)
		else:
			messages.warning(request, "Impossible de répondre à votre demande")
		
	# for filtering option
	if(request.GET.get('date') == 'desc'):
		items = items.order_by('-created_at')
	elif(request.GET.get('date') == 'asc'):
		items = items.order_by('created_at')

	if(request.GET.get('title') == 'desc'):
		items = items.order_by('-title')
	elif(request.GET.get('title') == 'asc'):
		items = items.order_by('title')
		
	return render(request, template_name, {'form':form,'documentitems':items, 'document': document, 'slug': slug})	

class CaravansModelView(TemplateView):
	template_name = 'base/caravans_model.html'
	def get(self, request, *args, **kwargs):
		form = CaravaneModelForm
		implant_key = CaravaneImplantation.objects.filter(status=True)
		return render(request, self.template_name, {'form': form,'implant':implant_key})
	def post(self, request, *args, **kwargs):
		data = request.POST
		upload = request.FILES
		form = CaravaneModelForm(data, upload)
		ids = data['templates']
		implant_key = CaravaneImplantation.objects.filter(status=True)
		if form.is_valid():
			frm = form.save(commit=False)
			frm.user_id = request.user.id
			frm.save()
			if ids:
				ids = data['templates'].split(",")
				templates = TemplateUpload.objects.filter(id__in=ids).update(caravane=frm.id)
			mail_ids = settings.ADMINS
			subject = 'New caravane listed for approval.'
			sender = 'support@lacaravane.com'
			# Send mail for admin users
			if mail_ids:
				for name, email in mail_ids:
					send_html_email(subject,sender,email,'mail/caravane_submission.html',{ 'data': data })
			messages.success(request, "Votre caravane a bien été ajoutée. Elle est en attente d'approbation.")
			return redirect('caravans_view', pk=frm.id)
		else:
			get_images = ''
			if ids:
				id_list = data['templates'].split(",")
				get_images = TemplateUpload.objects.filter(id__in=id_list)
			messages.warning(request, "Impossible de répondre à votre demande")
			return render(request, self.template_name, {'form': form, 'ids': ids, 'images' : get_images,'implant':implant_key})

class CaravanView(TemplateView):
	template_name = 'base/caravans_view.html'
	def get(self, request, pk):
		caravane = get_object_or_404(Caravane, Q(pk=pk) & (Q(status=1) | Q(user_id=request.user.id)))
		return render(request, self.template_name, {'caravane': caravane})

class CaravanList(TemplateView):
	template_name = 'base/caravans_list.html'
	def get(self, request, *args, **kwargs):
		data = request.GET
		imp_name = None
		if data:
			custom_dict = {}
			for value in data:
				val = data.get(value)
				if val is not '':
					custom_dict[value] = val

			query_dict = QueryDict('')
			query_dict = query_dict.copy()
			query_dict.update(custom_dict)
			imp = request.GET.get('implantation_caravane') 
			if imp:
				imp_name = CaravaneImplantation.objects.get_or_none(pk=imp)
			
			caravanes = CaravaneFilter(query_dict, queryset=Caravane.objects.filter(status=1))
		else:
			caravanes = Caravane.objects.filter(status=1)
		advertisement = Advertisement.objects.get_or_none(position='center',status=True)
		search_form = CaravaneSearchForm(data)
		implant_key = CaravaneImplantation.objects.filter(status=True)
		return render(request, self.template_name, {'caravanes': caravanes, 'ad': advertisement, 'form': search_form,'implant':implant_key,'imp':imp_name})

class AddTemplate(TemplateView):
	template_name = 'base/add_template.html'
	def get(self, request, *args, **kwargs):
		return render(request, self.template_name)

def template_upload(request):
	if request.method == 'POST':
		temp = TemplateUpload()
		temp.user_id = request.user.id
		temp.template = request.FILES['file']
		temp.save()
		response_data = {}
		response_data = {'result': 'success', 'id': temp.id}
		return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)

class VideoList(TemplateView):

	template_name = 'base/video_list.html'
	def get(self, request):
		videos =VideoCategory.objects.filter(status=True).order_by('orderby')
		form = VideoModelForm
		videocomment=VideoCommentForm
		get_data = request.GET
		search_form = VideoSortForm(get_data)
		return render(request, self.template_name, {'form': form, 'videos':videos,'search_form':search_form,'videocomment':videocomment })

	def post(self, request, *args, **kwargs):
		if (request.method=='POST') and (request.POST.get('form_name')=='add_video'):
			data=request.POST
			form = VideoModelForm(data)
			videocomment=VideoCommentForm
			if form.is_valid():
				frm_data = form.save(commit=False)
				frm_data.user_id = request.user.id
				frm_data.save()
				mail_ids = settings.ADMINS
				subject = 'New video listed for approval.'
				sender = 'support@lacaravane.com'
				if mail_ids:
					for name, email in mail_ids:
						send_html_email(subject,sender,email,'mail/video_submission.html',{ 'data': data })
				messages.success(request, "Votre vidéo a bien été ajoutée. Elle est en attente d'approbation.")
				return redirect('video_list')
			else:
				videos =VideoCategory.objects.filter(status=True).order_by('orderby')
				get_data = request.GET
				search_form = VideoSortForm(get_data)
				messages.warning(request, "Impossible de répondre à votre demande")
				return render(request, self.template_name, {'form': form , 'videos': videos,'search_form':search_form,'videocomment':videocomment})

		elif (request.method=='POST') and (request.POST.get('form_name')=='video_comt'):
			form_data=request.POST
			form = VideoModelForm
			video_comt_form = VideoCommentForm(form_data)
			if video_comt_form.is_valid():
				frm = video_comt_form.save(commit=False)
				frm.user_id = request.user.id
				frm.save()
				messages.success(request, "Le commentaire de la vidéo a bien été ajouté.")
				return redirect('video_list')
			else:
				videos =VideoCategory.objects.filter(status=True).order_by('orderby')
				get_data = request.GET
				search_form = VideoSortForm(get_data)
				messages.warning(request, "Impossible de répondre à votre demande")
				return render(request, self.template_name, {'form': form,'videos': videos,'search_form':search_form,'videocomment':video_comt_form})		

class VideoCategoryList(TemplateView):

	template_name = 'base/video_category.html'

	def get(self, request, slug):
		video_type =VideoCategory.objects.get_or_none(slug=slug)
		videos = video_type.video.filter(status=True)
		if(request.GET.get('date') == 'desc'):
			videos = videos.order_by('-created_at')
		elif(request.GET.get('date') == 'asc'):
			videos = videos.order_by('created_at')
		if(request.GET.get('name') == 'desc'):
			videos = videos.order_by('-name')
		elif(request.GET.get('name') == 'asc'):
			videos = videos.order_by('name')
		
		if videos is None:
			raise Http404
		form = VideoModelForm
		videocomment=VideoCommentForm
		get_data = request.GET
		search_form = VideoSortForm(get_data)
		return render(request, self.template_name, {'form': form ,'video_type':video_type,'videos': videos,'search_form':search_form,'videocomment':videocomment})

	def post(self, request,slug, *args, **kwargs):
		if (request.method=='POST') and (request.POST.get('form_name')=='add_video'):
			data=request.POST
			form = VideoModelForm(data)
			videocomment=VideoCommentForm
			if form.is_valid():
				frm_data = form.save(commit=False)
				frm_data.user_id = request.user.id
				frm_data.save()
				mail_ids = settings.ADMINS
				subject = 'New video listed for approval.'
				sender = 'support@lacaravane.com'
				if mail_ids:
					for name, email in mail_ids:
						send_html_email(subject,sender,email,'mail/video_submission.html',{ 'data': data })
				messages.success(request, "Votre vidéo a bien été ajoutée. Elle est en attente d'approbation.")
				return redirect('video_list')
			else:
				video_type =VideoCategory.objects.get_or_none(slug=slug)
				videos = video_type.video.filter(status=True)
				get_data = request.GET
				search_form = VideoSortForm(get_data)
				messages.warning(request, "Impossible de répondre à votre demande")
				return render(request, self.template_name, {'form': form ,'video_type':video_type,'videos': videos,'search_form':search_form,'videocomment':videocomment})

		elif (request.method=='POST') and (request.POST.get('form_name')=='video_comt'):
			form_data=request.POST
			form = VideoModelForm
			video_comt_form = VideoCommentForm(form_data)
			if video_comt_form.is_valid():
				frm = video_comt_form.save(commit=False)
				frm.user_id = request.user.id
				frm.save()
				messages.success(request, "Le commentaire de la vidéo a bien été ajouté.")
				video_type =VideoCategory.objects.get_or_none(slug=slug)
				videos = video_type.video.filter(status=True)
				get_data = request.GET
				search_form = VideoSortForm(get_data)
				return render(request, self.template_name, {'form': form,'video_type':video_type,'videos': videos,'search_form':search_form,'videocomment':video_comt_form})
			else:
				video_type =VideoCategory.objects.get_or_none(slug=slug)
				videos = video_type.video.filter(status=True)
				get_data = request.GET
				search_form = VideoSortForm(get_data)
				messages.warning(request, "Impossible de répondre à votre demande")
				return render(request, self.template_name, {'form': form,'video_type':video_type,'videos': videos,'search_form':search_form,'videocomment':video_comt_form})
					
def get_sites(request):
	sites = Site.objects.filter(status=1)
	sort_form = SortForm(request.GET)
	if request.GET.get('date') == 'desc':
		if request.GET.get('date') == 'desc':
			sites = sites.order_by('-created_at')
		elif request.GET.get('date') == 'asc':
			sites = sites.order_by('created_at')
		if request.GET.get('name') == 'desc':
			sites = sites.order_by('-site_name')
		elif request.GET.get('name') == 'asc':
			sites = sites.order_by('site_name')
	return sites, sort_form

class SiteList(TemplateView):
	template_name = 'base/add_site.html'
	def get(self, request, *args, **kwargs):
		form = SiteForm()
		sites, sort_form = get_sites(request)
		return render(request, self.template_name, { 'form': form, 'sites': sites, 'sort_form': sort_form })
	def post(self, request, *args, **kwargs):
		if request.method == 'POST':
			data = request.POST
			upload = request.FILES
			form = SiteForm(data, upload)
			sites, sort_form = get_sites(request)
			if form.is_valid():
				frm = form.save(commit=False)
				frm.user_id = request.user.id
				frm.save()
				messages.success(request, "Votre demande a été transmise avec succès, elle sera traitée dans les meilleurs délais.")
			else:
				messages.warning(request, "Impossible de répondre à votre demande")
				return render(request, self.template_name, {'form': form, 'sites': sites, 'sort_form': sort_form })
		return redirect('site_list')

class StaticPages(TemplateView):
	template_name = "base/cms.html"	
	def get(self, request, slugs):
		menu = MenuItem.objects.get_or_none(slug=slugs)
		if slugs =='team':
			papers = Newspaper.objects.filter(status=1)
		else:
			papers=None
			
		if menu is None:
			raise Http404
		return render(request, self.template_name, { 'content': menu.page, 'papers':papers })

class ForumPage(TemplateView):
	template_name="base/forum.html"

	def get(self,request):
		text='wellcome'
		return render(request, self.template_name, { 'text': text })

class MeetingsPage(TemplateView):
	template_name="base/meeting.html"

	def get(self, request, *args, **kwargs):
		meeting=Meeting.objects.extra({'start_date':"year(start_date)"}).values('start_date').annotate(count=Count('id')).filter(~Q(meeting_status=0))
		listing =[]
		for mt in meeting:
			sub_list = []
			list_meeting =  Meeting.objects.filter(start_date__year=mt['start_date']).filter(~Q(meeting_status=0)).filter(start_date__gte=datetime.date.today())
			sub_list ={'year' : mt['start_date'],'count' : mt['count'],'meetings_list':list_meeting}
			listing.append(sub_list)
		return render(request, self.template_name,{'meetings':listing })

class PreviousMeetingsPage(TemplateView):
	template_name="base/previousmeeting.html"

	def get(self, request, *args, **kwargs):
		meeting=Meeting.objects.extra({'start_date':"year(start_date)"}).values('start_date').annotate(count=Count('id')).filter(meeting_status=2)
		listing =[]
		for mt in meeting:
			sub_list = []
			list_meeting =  Meeting.objects.filter(start_date__year=mt['start_date']).filter(~Q(meeting_status=0))
			sub_list ={'year' : mt['start_date'],'count' : mt['count'],'meetings_list':list_meeting}
			listing.append(sub_list)
		return render(request, self.template_name,{'meetings':listing })

	
class Meetingview(TemplateView):
	template_name="base/viewmeeting.html"
	
	def get(self, request,slug):
		meeting=Meeting.objects.get_or_none(slug=slug)
		if request.user:
			user = request.user.id
			cnt = meeting.meeting.filter(user=user)
		else:
			cnt = None
		return render(request, self.template_name,{'meeting':meeting ,'status': cnt})


class ClassifiedWithCategory(TemplateView):

	template_name = "base/classified.html"

	def get(self,request):
		banner = BannerImage.objects.filter(status=True).order_by('-id')[:1]
		node = ClassifiedCategory.objects.filter(status=True).order_by('sort','tree_id')
		latest = Classified.objects.filter(status=True).order_by('-id')[:5]
		return render(request, self.template_name,{'nodes':node,'latests':latest,'banner':banner})

class Classifiedview(TemplateView):
	template_name = "base/classified_view.html"

	def get(self,request,slug):
		form=ClassfifiedSearchForm
		class_category =ClassifiedCategory.objects.get(slug=slug)
		classifieds = class_category.sub_classified.filter(status=True)
		main_category =ClassifiedCategory.objects.get(pk=class_category.parent_id)
		banner = BannerImage.objects.filter(status=True).order_by('-id')[:1]
		return render(request, self.template_name,{'classifieds':classifieds,'category':class_category,'form':form,'main_category':main_category,'banner':banner })

class ClassifiedModelView(TemplateView):
	template_name = "base/add_classified.html"

	def get(self,request):
		form = ClassifiedModelForm
		implant_key = CaravaneImplantation.objects.filter(status=True)
		banner = BannerImage.objects.filter(status=True).order_by('-id')[:1]
		return render(request, self.template_name,{ 'form':form,'implant':implant_key,'banner':banner })

	def post(self, request, *args, **kwargs):
		data = request.POST
		upload = request.FILES
		form = ClassifiedModelForm(data, upload)
		implant_key = CaravaneImplantation.objects.filter(status=True)
		ids = data['classified']
		if form.is_valid():
			frm = form.save(commit=False)
			frm.user_id = request.user.id
			frm.save()
			if ids:
				ids = data['classified'].split(",")
				templates = ClassifiedImage.objects.filter(id__in=ids).update(classified=frm.id)
			mail_ids = settings.ADMINS
			subject = 'Votre petite annonce va être approuvée dans les plus brefs délais.'
			sender = 'support@lacaravane.com'
			# Send mail for admin users
			if mail_ids:
				for name, email in mail_ids:
					send_html_email(subject,sender,email,'mail/classified_submission.html',{ 'data': data })
			messages.success(request, "Votre petite annonce va être approuvée dans les plus brefs délais")
			return redirect('classified')
		else:
			get_images = ''
			if ids:
				id_list = data['classified'].split(",")
				get_images = ClassifiedImage.objects.filter(id__in=id_list)
			messages.warning(request, "Impossible de répondre à votre demande")
			return render(request, self.template_name, {'form': form, 'ids': ids, 'images' : get_images,'implant':implant_key})

def classified_imag(request):
	if request.method == 'POST':
		img = ClassifiedImage()
		img.image = request.FILES['file']
		img.save()
		response_data = {}
		response_data = {'result': 'success', 'id': img.id}
		return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)

def destock_imag(request):
	if request.method == 'POST':
		img = DestockingImage()
		img.image = request.FILES['file']
		img.save()
		response_data = {}
		response_data = {'result': 'success', 'id': img.id}
		return HttpResponse(json.dumps(response_data), content_type="application/json", status=200)		


		
class ClassifiedDetails(TemplateView):
	template_name = "base/classified_details.html"

	def get(self,request,slug):
		details =Classified.objects.get(slug=slug)
		banner = BannerImage.objects.filter(status=True).order_by('-id')[:1]
		form_friend = ClassfifiedEmailForm
		if request.user:
			user = request.user.id
			cnt = details.favorites.filter(user=user)
			cunt = details.classified_abuse.filter(user=user)
		else:
			cnt = None	
			cunt = None
		return render(request, self.template_name,{'classifieds':details,'count':cnt,'cunt':cunt,'form_friend':form_friend,'banner':banner})

	def post(self, request,slug, *args, **kwargs):
		details =Classified.objects.get(slug=slug)
		form_friend = ClassfifiedEmailForm
		banner = BannerImage.objects.filter(status=True).order_by('-id')[:1]
		if request.user:
			user = request.user.id
			cnt = details.favorites.filter(user=user)
			cunt = details.classified_abuse.filter(user=user)
		else:
			cnt = None
			cunt = None

		if (request.method=='POST') and (request.POST.get('class_form')=='Add to favorite'):
			data = request.POST
			form = ClassifiedFavForm(data)
			if form.is_valid():
				frm = form.save(commit=False)
				frm.user_id = request.user.id
				frm.save()
				messages.success(request, "Classifié Ajouté à vos favoris")
			else:
				messages.warning(request, "Impossible de répondre à votre demande")
				return render(request, self.template_name, {'classifieds':details,'count':cnt,'cunt':cunt,'form_friend':form_friend,'banner':banner})

		elif (request.method=='POST') and (request.POST.get('class_form')=='Abus'):
			data = request.POST
			form = ClassifiedAbuseForm(data)
			if form.is_valid():
				frm = form.save(commit=False)
				frm.user_id = request.user.id
				frm.save()
				mail_ids = settings.ADMINS
				subject = 'classé signalé'
				sender = 'support@lacaravane.com'
				if mail_ids:
					for name, email in mail_ids:
						send_html_email(subject,sender,email,'mail/classified_abuse.html',{ 'data': details})
				messages.success(request, "classé signalé avec succès ")
			else:
				messages.warning(request, "Impossible de répondre à votre demande")
				return render(request, self.template_name, {'classifieds':details,'count':cnt,'cunt':cunt,'form_friend':form_friend,'banner':banner})		

		elif (request.method=='POST') and (request.POST.get('class_form')=='Email to friend'):
			data = request.POST
			email = request.POST.get('email')
			subject = 'Nouvelle petite ENVOYÉE de vous!'
			sender = 'support@lacaravane.com'
			if email:
				send_html_email(subject,sender,email,'mail/classified_abuse.html',{ 'data': details })
				messages.success(request, "annonce envoie avec succès ")
			else:
				messages.warning(request, "Impossible de répondre à votre demande")
				return render(request, self.template_name, {'classifieds':details,'count':cnt,'cunt':cunt,'form_friend':form_friend,'banner':banner})		
		return render(request, self.template_name, {'classifieds':details,'count':cnt,'cunt':cunt,'form_friend':form_friend,'banner':banner})	

#boutique  page
class MyAccountBoutiqueDashboard(TemplateView):		
	def get(self,request,*args,**kwargs):
		template_name = "base/dashboard.html"
		user = request.user.id
		user_type = UserProfile.objects.get_or_none(user_id=user)
		query = Query().from_table('phplist_user_user').where(email =request.user.email)
		userEx = query.select()
		user_profile = UserProfile.objects.get_or_none(user=user)
		form = AccountUserFrom(instance=user_profile)
		if not userEx:
			user_type.phplist = 0
			user_type.save();
			return render(request, template_name,{'form':form,'user_type':user_profile })
		return render(request, template_name,{'form':form,'user_type':user_profile })	

	def post(self, request,*args, **kwargs):
		template_name = "base/dashboard.html"
		data = request.POST
		form = AccountUserFrom(data)
		if form.is_valid():
			last_name=request.POST.get('last_name')
			first_name = request.POST.get('first_name')
			location = request.POST.get('location')
			city = request.POST.get('city')
			country = request.POST.get('country')
			latitude = request.POST.get('latitude')
			longitude = request.POST.get('longitude')
			political_short = request.POST.get('political_short')
			country_short = request.POST.get('country_short')
			department = request.POST.get('department')
			detail = UserProfile.objects.filter(user=request.user.id)
			if detail :
				detail.update(last_name=last_name,first_name=first_name,location=location,city=city,country=country,latitude=latitude,longitude=longitude,country_short= country_short,political_short=political_short,department=department)
			else:
				UserProfile.objects.create(user=request.user,last_name=last_name,first_name=first_name,location=location,city=city,country=country,latitude=latitude,longitude=longitude,country_short= country_short,political_short=political_short,department=department)	

			messages.success(request, "détails de votre compte mis à jour")
			return redirect('my_boutique_dashboard')
		else:
			messages.warning(request, "Impossible de répondre à votre demande")
			return render(request, self.template_name, {'form':form})	
		return render(request, self.template_name, {'form':form})




# destaocking caravane page
class MyAccountDealerDashboard(TemplateView):		
	def get(self,request,*args,**kwargs):
		template_name = "base/dashboard.html"
		user = request.user.id
		user_type = UserProfile.objects.get_or_none(user_id=user)
		query = Query().from_table('phplist_user_user').where(email =request.user.email)
		userEx = query.select()
		user_profile = UserProfile.objects.get_or_none(user=user)
		form = AccountUserFrom(instance=user_profile)
		if not userEx:
			user_type.phplist = 0
			user_type.save();
			return render(request, template_name,{'form':form,'user_type':user_profile })
		return render(request, template_name,{'form':form,'user_type':user_profile })	

	def post(self, request,*args, **kwargs):
		template_name = "base/dashboard.html"
		data = request.POST
		form = AccountUserFrom(data)
		if form.is_valid():
			last_name=request.POST.get('last_name')
			first_name = request.POST.get('first_name')
			location = request.POST.get('location')
			city = request.POST.get('city')
			country = request.POST.get('country')
			latitude = request.POST.get('latitude')
			longitude = request.POST.get('longitude')
			political_short = request.POST.get('political_short')
			country_short = request.POST.get('country_short')
			department = request.POST.get('department')
			detail = UserProfile.objects.filter(user=request.user.id)
			if detail :
				detail.update(last_name=last_name,first_name=first_name,location=location,city=city,country=country,latitude=latitude,longitude=longitude,country_short= country_short,political_short=political_short,department=department)
			else:
				UserProfile.objects.create(user=request.user,last_name=last_name,first_name=first_name,location=location,city=city,country=country,latitude=latitude,longitude=longitude,country_short= country_short,political_short=political_short,department=department)	

			messages.success(request, "détails de votre compte mis à jour")
			return redirect('my_dealer_dashboard')
		else:
			messages.warning(request, "Impossible de répondre à votre demande")
			return render(request, self.template_name, {'form':form})	
		return render(request, self.template_name, {'form':form})


class MyAccountDashboard(TemplateView):		
	def get(self,request,*args,**kwargs):
		user = request.user.id
		user_type = None
		try:
			user_type = UserProfile.objects.get_or_none(user_id=user)
		except:
			pass

		if not user_type:
			user_type  = UserProfile.objects.create(user=request.user)

		query = Query().from_table('phplist_user_user').where(email =request.user.email)
		userEx = query.select()
		if not userEx:
			user_type.phplist = False;
			user_type.save();

		if user_type.user_type ==1:
			destocks = Destocking.objects.filter(user=user)
			subs = None
			user_destock = None
			stock_enable = False
			try: 
				subs = Subscription.objects.get(purchaser_id=user, expiry_date__gte = datetime.date.today(), status=True)
				user_destock = Destocking.objects.filter(user_id=user,status=True,created_at__gte=subs.purchased_at).count()
			except:
				pass
			if subs:	
				if user_type.subscription and not user_type.deactivate and subs.expiry_date.date() >=datetime.date.today():
					stock_enable = True
			else:
				return redirect('my_dealer_dashboard')	
			template_name = "base/accounts_destock.html"
			return render(request, template_name,{'destocks':destocks,'user_type':user_type,'subs':subs,'user_destock':user_destock,'stock_enable':stock_enable })
		elif user_type.user_type ==2:
			subs = None
			user_product = None
			stock_enable = False
			try: 
				subs = Subscription.objects.get(purchaser_id=user, expiry_date__gte = datetime.date.today(), status=True)
				user_product = Product.objects.filter(user_id=user,status=True,created_at__gte=subs.purchased_at).count()
			except:
				pass
			if subs:	
				if user_type.subscription==True and user_type.deactivate==False and subs.expiry_date.date() >=datetime.date.today():
					stock_enable = True
			else: 
				return redirect('my_boutique_dashboard')	

			template_name = "base/accounts_boutique.html"		
			return render(request, template_name,{'user_type':user_type,'subs':subs,'user_destock':user_product,'stock_enable':stock_enable })
		else:
			template_name = "base/dashboard.html"
			user_profile = UserProfile.objects.get_or_none(user=user)
			form = AccountUserFrom(instance=user_profile)
			return render(request, template_name,{'form':form,'user_type':user_profile })

	def post(self, request,*args, **kwargs):
		template_name = "base/dashboard.html"
		data = request.POST
		form = AccountUserFrom(data)
		user_type = UserProfile.objects.get_or_none(user_id=request.user.id)
		if form.is_valid():
			last_name=request.POST.get('last_name')
			first_name = request.POST.get('first_name')
			location = request.POST.get('location')
			city = request.POST.get('city')
			country = request.POST.get('country')
			latitude = request.POST.get('latitude')
			longitude = request.POST.get('longitude')
			political_short = request.POST.get('political_short')
			country_short = request.POST.get('country_short')
			department = request.POST.get('department')
			detail = UserProfile.objects.filter(user=request.user.id)
			if detail :
				detail.update(last_name=last_name,first_name=first_name,location=location,city=city,country=country,latitude=latitude,longitude=longitude,country_short= country_short,political_short=political_short,department=department)
			else:
				UserProfile.objects.create(user=request.user,last_name=last_name,first_name=first_name,location=location,city=city,country=country,latitude=latitude,longitude=longitude,country_short= country_short,political_short=political_short,department=department)	

			messages.success(request, "détails de votre compte mis à jour")
			if user_type.user_type =='1':
				return redirect('my_dealer_dashboard')
			elif user_type.user_type =='2':
				return redirect('my_boutique_dashboard')
			else:
				return redirect('my_dashboard')	
		else:
			messages.warning(request, "Impossible de répondre à votre demande")
			return render(request, template_name, {'form':form})	
		return render(request, template_name, {'form':form})

# for destock
class DestockAccountview(TemplateView):	
	template_name = "base/accounts_destock_new.html"
	def get(self, request, pk):
		subs = Subscription.objects.get(pk=pk)
		form = subscriptionForm(instance= subs)
		offers = Offer.objects.filter(status=True, offer_type=1) 
		return render(request, self.template_name,{'form':form,'offers':offers,'sub_id':pk,'subs':subs})
	def post(self, request,pk):
		form = subscriptionForm(request.POST)	
		if request.POST.get('subs_id'):	
			editsub = Subscription.objects.filter(pk=request.POST.get('subs_id'))
			edit = editsub.update(campany_address=request.POST.get('campany_address'),campany_post=request.POST.get('campany_post'),campany_state=request.POST.get('campany_state'),campany_url=request.POST.get('campany_url'),client_email=request.POST.get('client_email'),client_fname=request.POST.get('client_fname'),payment_method=request.POST.get('payment_method'), purchaser_id=request.user.id,title = request.POST.get('title'), company_name=request.POST.get('company_name'),manager_name=request.POST.get('manager_name'), email=request.POST.get('email'), contact_number=request.POST.get('contact_number'),country=request.POST.get('country'),status=True, offer_destock_id=request.POST.get('offer_destock'),campany_latitude=request.POST.get('campany_latitude'),campany_longitude=request.POST.get('campany_longitude'))
			messages.success(request, "abonnement fait avec succès")
			return redirect('my_dashboard')	
		else:
			messages.warning(request, "Impossible de répondre à votre demande")	
			return render(request, self.template_name,{'warning':'Impossible de répondre à votre demande','form':form})

#for boutique
class BoutiqueAccountview(TemplateView):	
	template_name = "base/accounts_boutique_new.html"
	def get(self, request, pk):
		subs = Subscription.objects.get(pk=pk)
		form = subscriptionForm(instance=subs)
		offers = Offer.objects.filter(status=True) 
		return render(request, self.template_name,{'form':form,'offers':offers,'sub_id':pk,'subs':subs})
	def post(self, request,pk):
		form = subscriptionForm(request.POST)	
		if request.POST.get('subs_id'):	
			editsub = Subscription.objects.filter(pk=request.POST.get('subs_id'))
			edit = editsub.update(campany_address=request.POST.get('campany_address'),campany_post=request.POST.get('campany_post'),campany_state=request.POST.get('campany_state'),campany_url=request.POST.get('campany_url'),client_email=request.POST.get('client_email'),client_fname=request.POST.get('client_fname'),payment_method=request.POST.get('payment_method'), purchaser_id=request.user.id,title = request.POST.get('title'), company_name=request.POST.get('company_name'),manager_name=request.POST.get('manager_name'), email=request.POST.get('email'), contact_number=request.POST.get('contact_number'),country=request.POST.get('country'),status=True, offer_product_id=request.POST.get('offer_product'),campany_latitude=request.POST.get('campany_latitude'),campany_longitude=request.POST.get('campany_longitude'))
			messages.success(request, "abonnement fait avec succès")
			return redirect('my_dashboard')	
		else:
			messages.warning(request, "Impossible de répondre à votre demande")	
			return render(request, self.template_name,{'warning':'Impossible de répondre à votre demande','form':form})




class DocumentMyView(TemplateView):

	template_name = "base/accounts_document.html"

	def get(self,request,*args,**kwargs):
		user = request.user.id
		user_type = UserProfile.objects.get_or_none(user_id=user)
		docs_items = DocumentItem.objects.filter(user=user)
		return render(request, self.template_name,{'docs':docs_items,'user_type':user_type })

class CaravaneMyView(TemplateView):

	template_name = "base/accounts_caravane.html"

	def get(self,request,*args,**kwargs):
		user = request.user.id
		user_type = UserProfile.objects.get_or_none(user_id=user)
		caravanes = Caravane.objects.filter(user=user)
		return render(request, self.template_name,{'caravanes':caravanes,'user_type':user_type })

class MeetingMyView(TemplateView):

	template_name = "base/accounts_meeting.html"
	def get(self,request,*args,**kwargs):
		user = request.user.id
		user_type = UserProfile.objects.get_or_none(user_id=user)
		listing =[]
		meeting = Meeting.objects.filter(~Q(meeting_status=0))
		for mt in meeting:
			sub_list = []
			commit = MeetingRegistrationForm.objects.filter(user=user).filter(meeting=mt.id)
			if commit:
				booked = commit
			else:
				booked = None
			sub_list ={'meeting' :mt,'book' : booked }
			listing.append(sub_list)		
		return render(request, self.template_name,{'listing':listing,'user_type':user_type })

class ClassisfiedMyView(TemplateView):
	template_name = "base/accounts_classified.html"

	def get(self,request,*args,**kwargs):
		user = request.user.id
		user_type = UserProfile.objects.get_or_none(user_id=user)
		classifieds = Classified.objects.filter(user=user)
		return render(request, self.template_name,{'classifieds':classifieds,'user_type':user_type})

class DestockMyListView(TemplateView): 
	template_name = "base/accounts_destock_list.html"

	def get(self,request,*args,**kwargs):
		user = request.user.id
		user_type = UserProfile.objects.get_or_none(user_id=user)
		destocks = Destocking.objects.filter(user=user)
		enable_user = False
		subs= Subscription.objects.filter(purchaser_id =user).order_by('-id')[:1]
		count = Destocking.objects.filter(user=user,status=True).count()
		for sub in subs:	
			if sub.offer_destock.number_of_caravanes >count:
				enable_user = True		
		return render(request, self.template_name,{'destocks':destocks,'user_type':user_type,'enable_user':enable_user})

class DestockAccountBlock(TemplateView):
	template_name = "base/accounts_destock_block.html"
	def get(self, request):
		return render(request, self.template_name)

class DestockUnauth(TemplateView):
	template_name = "base/unauth_destock.html"
	def get(self, request):
		return render(request, self.template_name)

class BoutiqueUnauth(TemplateView):
	template_name = "base/unauth_boutiqu.html"
	def get(self, request):
		return render(request, self.template_name)				

		
class ProductAccountBlock(TemplateView):
	template_name = "base/accounts_product_block.html"
	def get(self, request):
		return render(request, self.template_name)



## New chanages --Destocking caravane
class DestockMyView(TemplateView):
	template_name = "base/accounts_destock_new.html"
	def get(self, request):
		if not request.user.is_authenticated():
			return redirect('un_auth_destock')
		try:
			user_type = UserProfile.objects.get_or_none(user_id=request.user.id)
			if user_type.user_type ==2:
				return redirect('block_destock_page')
		except:
			user_type =None
		form = subscriptionForm()
		offers = Offer.objects.filter(status=True) 
		return render(request, self.template_name,{'form':form,'offers':offers,'user_type':user_type})

	def post(self, request):
		exp_date = datetime.datetime.now()+datetime.timedelta(+30)
		post_data = request.POST
		form = subscriptionForm(post_data)
		user = request.user.id
		user_type = UserProfile.objects.get_or_none(user_id=user)
		offers = Offer.objects.filter(status=True)
		try:
			siteinfo = Siteinfo.objects.get_or_none(name='lacaravane')
		except:
			siteinfo = None 	
		
		if form.is_valid():
			old_sub = Subscription.objects.filter(purchaser_id=request.user.id).update(status=False)
			frm = form.save(commit=False)
			frm.user_id = request.user.id
			frm.expiry_date = exp_date
			frm.status = True
			frm.save()
			user_type.user_type = 1
			user_type.save()
			if siteinfo.notify_email:
				data = {'purchaser':request.user.username,'company_name':post_data.get('company_name'),'manager_name':post_data.get('manager_name'),'campany_city':post_data.get('campany_city'),'country':post_data.get('country')}
				subject = "déstockage formulaire d'inscription demandeur"
				sender = 'support@lacaravane.com'
				send_html_email(subject,sender,siteinfo.notify_email,'mail/subscription_submit.html',{ 'data': data })
			messages.success(request, "abonnement fait avec succès")
			return redirect('my_dashboard')
		else:
			messages.warning(request, "Impossible de répondre à votre demande")	
			return render(request, self.template_name,{'warning':'Impossible de répondre à votre demande','form':form,'offers':offers,'user_type':user_type})

#Boutique
class BoutiqueMyView(TemplateView):
	template_name = "base/accounts_boutique_new.html"
	def get(self, request):
		if not request.user.is_authenticated():
			return redirect('un_auth_product')
		try:	
			user_type = UserProfile.objects.get_or_none(user_id=request.user.id)
			if user_type.user_type ==1:
				return redirect('block_product_page')
		except:
			user_type =None

		form = subscriptionForm()
		offers = Offer.objects.filter(status=True) 
		return render(request, self.template_name,{'form':form,'offers':offers,'user_type':user_type})

	def post(self, request):
		exp_date = datetime.datetime.now()+datetime.timedelta(+30)
		post_data = request.POST
		form = subscriptionForm(post_data)
		user = request.user.id
		user_type = UserProfile.objects.get_or_none(user_id=user)
		offers = Offer.objects.filter(status=True) 
		try:
			siteinfo = Siteinfo.objects.get_or_none(name='lacaravane')
		except:
			siteinfo = None

		if form.is_valid():
			old_sub = Subscription.objects.filter(purchaser_id=request.user.id).update(status=False)
			frm = form.save(commit=False)
			frm.user_id = request.user.id
			frm.expiry_date = exp_date
			frm.status = True
			frm.save()
			user_type.user_type = 2
			user_type.save()
			if siteinfo.notify_email:
				data = {'purchaser':request.user.username,'company_name':post_data.get('company_name'),'manager_name':post_data.get('manager_name'),'campany_city':post_data.get('campany_city'),'country':post_data.get('country')}
				subject = "déstockage formulaire d'inscription demandeur"
				sender = 'support@lacaravane.com'
				send_html_email(subject,sender,siteinfo.notify_email,'mail/subscription_submit.html',{ 'data': data })
			messages.success(request, "abonnement fait avec succès")
			return redirect('my_dashboard')
		else:
			messages.warning(request, "Impossible de répondre à votre demande")	
			return render(request, self.template_name,{'warning':'Impossible de répondre à votre demande','form':form,'offers':offers,'user_type':user_type})


##End
class ClassisfiedMyFavorites(TemplateView):
	template_name = "base/accounts_fav_classified.html"
	def get(self,request,*args,**kwargs):
		user = request.user.id
		user_type = UserProfile.objects.get_or_none(user_id=user)
		adds = ClassifiedFavorite.objects.filter(user=user)
		return render(request, self.template_name,{'classifieds':adds,'user_type':user_type }) #fav_product.html

class DestockMyFavView(TemplateView):
	template_name = "base/accounts_favdestock.html"
	def get(self,request,*args,**kwargs):
		user = request.user.id
		user_type = UserProfile.objects.get_or_none(user_id=user)
		destocks = DestockingFavorite.objects.filter(user=user)
		return render(request, self.template_name,{'destocks':destocks,'user_type':user_type})

class ProductMyFavView(TemplateView):
	template_name = "base/fav_product.html"
	def get(self,request,*args,**kwargs):
		user = request.user.id
		user_type = UserProfile.objects.get_or_none(user_id=user)
		product = ProductFavorite.objects.filter(user=user)
		return render(request, self.template_name,{'products':product,'user_type':user_type})			

class ProductMyView(TemplateView):
	template_name = "base/accounts_shop.html"	

	def get(self,request,*args,**kwargs):
		if not request.user.is_authenticated():
			return redirect('un_auth_product')
		try:
			user_type = UserProfile.objects.get_or_none(user_id=request.user.id)
			if user_type.user_type ==1:
				return redirect('block_product_page')
		except:
			user_type =None

		enable_user = False
		user = request.user.id
		subs= Subscription.objects.filter(purchaser_id =user).order_by('-id')[:1]
		count = Product.objects.filter(user=user,status=True).count()
		for sub in subs:	
			if sub.offer_product.number_of_caravanes >count:
				enable_user = True
		user_type = UserProfile.objects.get_or_none(user_id=user)
		shops = Product.objects.filter(user=user)
		return render(request, self.template_name,{'shops':shops,'user_type':user_type,'enable_user':enable_user})		

class videoMyView(TemplateView):
	template_name = "base/accounts_video.html"

	def get(self,request,*args,**kwargs):
		user = request.user.id
		user_type = UserProfile.objects.get_or_none(user_id=user)
		videos = Video.objects.filter(user=user)
		return render(request, self.template_name,{'videos':videos,'user_type':user_type })

class ClassifiedSearch(TemplateView):
	template_name = "base/classified_search.html"

	def get(self,request,*args,**kwargs):
		data = request.GET
		classifieds = {}
		if data:
			custom_dict = {}
			for value in data:
				val = data.get(value)
				if val is not '':
					if value =='price':
						try:
							rang = ClassifiedPriceRange.objects.get(pk=val)
							custom_dict[value]={ unicode(rang.price_start),unicode(rang.price_end) }
						except:
							pass
					else:	
						custom_dict[value] = val

			query_dict = QueryDict('')
			query_dict = query_dict.copy()
			query_dict.update(custom_dict)
			classifieds = ClassifiedFilter(query_dict, queryset=Classified.objects.all())
		return render(request, self.template_name,{'classifieds':classifieds })			

class SiteMyView(TemplateView):
	template_name = "base/accounts_mysite.html"

	def get(self,request,*args,**kwargs):
		user = request.user.id
		user_type = UserProfile.objects.get_or_none(user_id=user)
		sites = Site.objects.filter(user=user)
		return render(request, self.template_name,{'sites':sites,'user_type':user_type})

class CheckLogin(View):

	def post(self, request, *args, **kwargs):
		response = {'status': False,'user_id':None}
		try:
			sess = Session.objects.get(pk=request.POST.get('session_id'))
			print(sess)
		except Session.DoesNotExist:
			return HttpResponse(json.dumps(response), content_type='application/json')

		data = sess.get_decoded()
		user = User.objects.get(pk=data['_auth_user_id'])
		if user:
			response['status'] = True
			response['user_id'] = data['_auth_user_id']
		else:
			response['status'] = False
			response['user_id'] = None
		return JsonResponse(response)

	def get(self, request, *args, **kwargs):
		return self.post(request, *args, **kwargs)

class MeetingPartnerOfferview(TemplateView):
	template_name = "base/meeting_offer.html"

	def get(self,request,slug):
		meeting=Meeting.objects.get_or_none(slug=slug)
		offers = meeting.meeting_offer.filter(status=True)
		return render(request, self.template_name,{'meeting':meeting,'offers':offers })

class MeetingRegisterview(TemplateView):

	template_name = "base/meeting_register_form.html"

	def get(self,request,slug):
		form = MeetingRegForm()
		meeting=Meeting.objects.get_or_none(slug=slug)
		total = meeting.meeting.filter(status=True).count()
		if request.user:
			user = request.user.id
			cnt = meeting.meeting.filter(user=user)
		else:
			cnt = None
		return render(request, self.template_name,{'meeting':meeting,'form':form,'status': cnt,'total': total })

	def post(self, request,slug, *args, **kwargs):
		meeting=Meeting.objects.get_or_none(slug=slug)
		total = meeting.meeting.filter(status=True).count()
		if request.user:
			user = request.user.id
			cnt = meeting.meeting.filter(user=user)
		else:
			cnt = None
		if request.method == 'POST':
			data = request.POST
			form = MeetingRegForm(data)
			if form.is_valid():
				frm = form.save(commit=False)
				frm.user_id = request.user.id
				frm.save()
				mail_ids = settings.ADMINS
				subject = 'Meeting booked and waiting for approval.'
				sender = 'support@lacaravane.com'
				if mail_ids:
					for name, email in mail_ids:
						send_html_email(subject,sender,email,'mail/meeting_submission.html',{ 'data': meeting })
				messages.success(request, "Réservé avec succès et est en attente d'approbation ")
			else:
				messages.warning(request, "Impossible de répondre à votre demande")
				return render(request, self.template_name, {'meeting':meeting,'form':form,'status': cnt,'total': total})
		return redirect('meeting')		

class MeetingActivitesview(TemplateView):

	template_name = "base/meeting_activites.html"
	
	def get(self,request,slug):
		meeting=Meeting.objects.get_or_none(slug=slug)
		offers = meeting.meeting_activity.filter(status=True)
		if request.user:
			user = request.user.id
			cnt = meeting.meeting.filter(user=user)
		else:
			cnt = None
		return render(request, self.template_name,{'meeting':meeting,'activities':offers,'status': cnt})

class Geolocalview(TemplateView):
	template_name = "base/new_geo_local.html"

	def get(self,request):
		list_user = UserProfile.objects.values('country_short').annotate(dcount=Count('country_short'))
		return render(request, self.template_name,{'lists': list_user})
class GeolocalFranceview(TemplateView):
	template_name = "base/geo_france_dept.html"

	def get(self,request):
		lists = UserProfile.objects.values('department').annotate(dcount=Count('department')).filter(country_short ='FR')
		return render(request, self.template_name,{'lists': lists})

class ProductView(TemplateView):
	template_name = "base/product_list.html"

	def get(self,request):
		product =ProductCategory.objects.filter(status=True).order_by('name')
		user_type = UserProfile.objects.get_or_none(user_id=request.user.id)
		return render(request, self.template_name,{'products': product,'user_type':user_type})

class ProductCategoryView(TemplateView):
	template_name = "base/product_category.html"

	def get(self,request,slug):
		product_category =ProductCategory.objects.get_or_none(slug=slug)
		product = product_category.products.filter(status=True,user__profile__subscription=1).order_by('name')
		return render(request, self.template_name,{'category':product_category,'products': product})		

class ProductModelView(TemplateView):
	template_name = "base/productform.html"

	def get(self,request):
		form = ProductModelForm()
		return render(request, self.template_name,{'form':form})

	def post(self,request):
		if request.method == 'POST':
			post_data = request.POST;
			form = ProductModelForm(post_data,request.FILES)
			if form.is_valid():
				frm = form.save(commit=False)
				frm.user_id = request.user.id
				frm.save()
				try:
					siteinfo = Siteinfo.objects.get_or_none(name='lacaravane')
				except:
					siteinfo = None 
				if siteinfo.notify_email:
					data = {'user':request.user.username,'product_name':post_data.get('name'),'description':post_data.get('description'),'price':post_data.get('price'),'availability':post_data.get('availability')}
					subject = "Nouveau produit ajouté avec succès"
					sender = 'support@lacaravane.com'
					send_html_email(subject,sender,siteinfo.notify_email,'mail/product_submit.html',{ 'data': data })
				messages.success(request, "Nouveau produit ajouté avec succès")
			else:
				messages.warning(request, "Impossible de répondre à votre demande")
				return render(request, self.template_name, {'form':form})
		return redirect('products')

class ProductDetailView(TemplateView):
	template_name = "base/product_view.html"

	def get(self,request,slug):
		product = Product.objects.get_or_none(slug=slug)
		if request.user:
			user = request.user.id
			abus = product.product_abuse.filter(user=user).count()
			fave = product.product_fav.filter(user=user).count()
		else:	
			abus = None
			fave = None

		mail_form = ProductEmailForm()
		return render(request, self.template_name,{'product':product,'mail_form':mail_form,'ab_status':abus,'fav':fave })

	def  post(self,request,slug):
		product =Product.objects.get_or_none(slug=slug)

		if request.user:
			user = request.user.id
			abus = product.product_abuse.filter(user=user).count()
			fave = product.product_fav.filter(user=user).count()
		else:	
			abus = None
			fave = None

		if (request.method=='POST') and (request.POST.get('form_type')=='email'):
			mail_form = ProductEmailForm(request.POST)
			data = request.POST
			email = request.POST.get('email')
			subject = 'Nouveau produit recommandé !'
			sender = 'support@lacaravane.com'
			if email:
				send_html_email(subject,sender,email,'mail/tell_friend.html',{ 'data': product })
				messages.success(request, "annonce envoie avec succès ")
			else:
				messages.warning(request, "Impossible de répondre à votre demande")
				return render(request, self.template_name, {'product':product,'mail_form':mail_form,'ab_status':abus,'fav':fave})
		if (request.method=='POST') and (request.POST.get('form_type')=='abus'):
			data = request.POST
			form = ProductAbuseForm(data)
			if form.is_valid():
				frm = form.save(commit=False)
				frm.user_id = request.user.id
				frm.save()
				mail_ids = settings.ADMINS
				subject = 'des rapports de produits'
				sender = 'support@lacaravane.com'
				if mail_ids:
					for name, email in mail_ids:
						send_html_email(subject,sender,email,'mail/product_abuse.html',{ 'data': product})
				messages.success(request, "produit signalé avec succès ")
			else:
				messages.warning(request, "Impossible de répondre à votre demande")
				return render(request, self.template_name, {'product':product,'mail_form':mail_form,'ab_status':abus,'fav':fave})
		return redirect('products')



class ClassifiedDelete(TemplateView):

	def get(self,request,slug):
		add =Classified.objects.get_or_none(slug=slug).delete()
		messages.success(request, "ajouter supprimé avec succès!")	
		return redirect('my_classified')

class ClassifiedEdit(TemplateView):
	template_name = "base/classified_edit.html"

	def get(self,request,slug):
		classified =Classified.objects.get(slug=slug)
		form = ClassifiedModelForm(instance=classified)
		implant_key = CaravaneImplantation.objects.filter(status=True)
		banner = BannerImage.objects.filter(status=True).order_by('-id')[:1]
		return render(request, self.template_name,{ 'form':form,'implant':implant_key,'banner':banner,'classified':classified })
		
	def post(self, request,slug, *args, **kwargs):
		data = request.POST
		upload = request.FILES
		form = ClassifiedModelForm(data, upload)
		implant_key = CaravaneImplantation.objects.filter(status=True)
		banner = BannerImage.objects.filter(status=True).order_by('-id')[:1]
		ids = data['classified']
		add_id = request.POST.get('id')
		if form.is_valid():
			title=request.POST.get('title')
			description = request.POST.get('description')
			category = request.POST.get('category')
			department = request.POST.get('department')
			brand = request.POST.get('brand')
			model = request.POST.get('model')
			price = request.POST.get('price')
			year = request.POST.get('year')
			phone = request.POST.get('phone')
			email = request.POST.get('email')
			
			country = request.POST.get('country')
			implantation = request.POST.get('implantation')
			latitude = request.POST.get('latitude')
			longitude = request.POST.get('longitude')
			city = request.POST.get('city')
			details = Classified.objects.filter(pk=add_id)
			if details:
				details.update(title=title,description=description,category=category,city=city,country=country,latitude=latitude,longitude=longitude,brand= brand,model=model,department=department,price=price,year=year,phone=phone,email=email,implantation=implantation)
			if ids:
				ids = data['classified'].split(",")
			templates = ClassifiedImage.objects.filter(id__in=ids).update(classified=add_id)
			messages.success(request, "ajouter à jour avec succès")
			return redirect('classified')
		else:
			get_images = ''
			if ids:
				id_list = data['classified'].split(",")
				get_images = ClassifiedImage.objects.filter(id__in=id_list)
			messages.warning(request, "Impossible de répondre à votre demande")
			#return render(request, self.template_name, {'form': form, 'ids': ids, 'images' : get_images,'implant':implant_key,'banner':banner})
			return redirect('my_classified')

class ClassifiedCategoryView(TemplateView):

	def get(self,request,pk):
		response = {}
		category =ClassifiedCategory.objects.filter(parent_id=pk)
		html= "<div class='form-group clearfix'><label class='control-label col-md-6 no-padd'></label><div class='col-md-5 no-padd'><select id='choose_class_subcategory' class='custom-selectize' name='sub_category'>"
		for cat in category:
			html +="<option value='%d'>%s</option>" % (cat.id,smart_str(cat.name))
		html +="</select></div></div>" 

		response['html'] = html
		return HttpResponse(json.dumps(response),content_type='application/json')

class GetDeptView(TemplateView):
	def get(self,request,slug):
		response = {}
		depts =ClassifiedDepartment.objects.filter(country=slug).order_by('name')
		html= "<select id='class_dept_selectize' class='custom-selectize' name='department'>"
		if depts:
			for dept in depts:
				html +="<option value='%d'>%s</option>" % (dept.id,smart_str(dept.name))
		else:
			html +="<option value=''>aucun départements</option>"
		html +="</select>"			 
		response['html'] = html
		return HttpResponse(json.dumps(response),content_type='application/json')

class DestockModelView(TemplateView):
	template_name = 'base/add_destock.html'
	def get(self,request):
		form = DestockModelForm
		implant_key = CaravaneImplantation.objects.filter(status=True)
		banner = BannerImage.objects.filter(status=True).order_by('-id')[:1]
		subs= Subscription.objects.filter(purchaser_id = request.user.id).order_by('-id')[:1]
		return render(request, self.template_name,{ 'form':form,'implant':implant_key,'banner':banner,'subs':subs })
		
	def post(self, request, *args, **kwargs):
		subs= Subscription.objects.filter(purchaser_id = request.user.id).order_by('-id')[:1]
		banner = BannerImage.objects.filter(status=True).order_by('-id')[:1]
		data = request.POST
		upload = request.FILES
		form = DestockModelForm(data, upload)
		implant_key = CaravaneImplantation.objects.filter(status=True)

		ids = data['destocking']
		if form.is_valid():
			frm = form.save(commit=False)
			frm.user_id = request.user.id
			frm.save()
			log_it.send(sender='MailtoAlert', message=data, level=frm.id)
			if ids:
				ids = data['destocking'].split(",")
				templates = DestockingImage.objects.filter(id__in=ids).update(destocking=frm.id)

			try:
				siteinfo = Siteinfo.objects.get_or_none(name='lacaravane')
			except:
				siteinfo = None 

			if siteinfo.notify_email:
				subject = 'Votre petite annonce va être approuvée dans les plus brefs délais.'
				sender = 'support@lacaravane.com'
				send_html_email(subject,sender,siteinfo.notify_email,'mail/destock_submission.html',{ 'data': data })
				# mail_ids = settings.ADMINS
				# subject = 'Votre petite annonce va être approuvée dans les plus brefs délais.'
				# sender = 'support@lacaravane.com'
				# # Send mail for admin users
				# if mail_ids:
				# 	for name, email in mail_ids:
				# 		send_html_email(subject,sender,email,'mail/classified_submission.html',{ 'data': data })
			messages.success(request, "Votre petite annonce va être approuvée dans les plus brefs délais")
			return redirect('view_destock')
		else:
			get_images = ''
			if ids:
				id_list = data['destocking'].split(",")
				get_images = DestockingImage.objects.filter(id__in=id_list)
			messages.warning(request, "Impossible de répondre à votre demande")
			return render(request, self.template_name, {'form': form, 'ids': ids, 'images' : get_images,'implant':implant_key,'banner':banner,'subs':subs })

class DestockView(TemplateView):
	template_name = "base/destocking_list.html"

	def get(self, request, *args, **kwargs):
		user=None
		subs = None
		user_destock = None
		imp_name = None
		user_type = None 
		user = request.user.id
		if user:
			user_type = UserProfile.objects.get_or_none(user_id=user)
			try: 
				subs = Subscription.objects.get(purchaser_id=user,expiry_date__gte = datetime.date.today(),status=True)
				user_destock = Destocking.objects.filter(user_id=user,status=True,created_at__gte=subs.purchased_at).count()
			except:
				pass				
		banner = BannerImage.objects.filter(status=True).order_by('-id')[:1]	
		data = request.GET
		if data:
			custom_dict = {}
			for value in data:
				val = data.get(value)
				if val is not '':
					custom_dict[value] = val

			query_dict = QueryDict('')
			query_dict = query_dict.copy()
			query_dict.update(custom_dict)
			imp = request.GET.get('implantation') 
			if imp:
				imp_name = CaravaneImplantation.objects.get_or_none(pk=imp)		
			destocks = DestockFilter(query_dict, queryset= Destocking.objects.filter(status=1,user__profile__subscription=1))

		else:
			destocks = Destocking.objects.filter(status=1,user__profile__subscription=1)
		form = DestockSearchForm(data)
		implant_key = CaravaneImplantation.objects.filter(status=True)
		user_type = UserProfile.objects.get_or_none(user_id=request.user.id)
		return render(request, self.template_name, {'destocks':destocks,'banner':banner,'form':form,'implant':implant_key,'imp':imp_name,'user_type':user_type,'subs':subs,'user_destock':user_destock,'user_type':user_type})

class DestockDetails(TemplateView):
	template_name = "base/destocking_details.html"
	def get(self,request,pk):
		try:
			xview = CaravaneContact.objects.filter(user =request.user.id,destock =pk,status=False).count()
			if xview<1:
				CaravaneContact.objects.create(user_id=request.user.id,destock_id=pk,status=False)
		except:
			pass
		
			
		cnt = None
		subs = None
		destock = Destocking.objects.get(pk=pk)
		try:
			cnt = destock.destock_fav.filter(user=request.user.id)
		except Exception, e:
			pass
		banner = BannerImage.objects.filter(status=True).order_by('-id')[:1]
		subs= Subscription.objects.filter(purchaser_id = destock.user.id).order_by('-id')[:1]
		if 'viewcount' in request.session:
			request.session['viewcount'] +=1
		else:	
			request.session['viewcount'] = 1

		return render(request, self.template_name,{'destock':destock,'banner':banner,'cnt':cnt,'subscription':subs })
	@login_required	
	def post(self,request,pk,*args, **kwargs):
		cnt = None
		banner = BannerImage.objects.filter(status=True).order_by('-id')[:1]
		destock = Destocking.objects.get(pk=pk)
		cnt = destock.destock_fav.filter(user=request.user.id)
		data = request.POST
		form = DestockFavForm(data)
		if form.is_valid():
			frm = form.save(commit=False)
			frm.user_id = request.user.id
			frm.save()
			messages.success(request, "caravane Ajouté à vos favoris")
		else:
			messages.warning(request, "Impossible de répondre à votre demande")
		return render(request, self.template_name,{'destock':destock,'banner':banner,'cnt':cnt })

# Django-Paypal AddForm
class MysalesArea(TemplateView):
	template_name = "base/mysalesarea.html"
	def get(self, request):
		form = MysaleForm()
		notify_url = settings.SITE_URL+reverse('paypal-ipn')
		offers = Offer.objects.filter(status=True) 
		return render(request, self.template_name,{'form':form,'offers':offers,'paypal_email':settings.PAYPAL_RECEIVER_EMAIL,'paypal_url':settings.PAYPAL_URL,'paypal_return_url':settings.PAYPAL_NOTIFY_URL,'success_url':settings.PAYPAL_RETURN_URL,'cancelled':settings.PAYPAL_CANCEL_URL,'notify_url':notify_url })

	def post(self, request):
		old_sub = Subscription.objects.filter(purchaser_id=request.user.id).update(status=False) 
		exp_date = datetime.datetime.now()+datetime.timedelta(+30)
		sub = Subscription.objects.create(offer_id=request.POST.get('os0'),campany_address=request.POST.get('campany_address'),campany_post=request.POST.get('campany_post'),campany_state=request.POST.get('campany_state'),campany_url=request.POST.get('campany_url'),client_email=request.POST.get('client_email'),client_fname=request.POST.get('client_fname'),payment_method=request.POST.get('payment_method'), purchaser_id=request.user.id, company_name=request.POST.get('campany_name'),manager_name=request.POST.get('manager_name'), email=request.POST.get('email'), contact_number=request.POST.get('phone'),country=request.POST.get('country'),status=True, expiry_date=exp_date,purchased_at=datetime.datetime.now(),campany_city=request.POST.get('campany_city'),campany_latitude=request.POST.get('campany_latitude'),campany_longitude=request.POST.get('campany_longitude'))
		if(sub):
			messages.success(request, "abonnement fait avec succès")
			return redirect('my_destock')
		else:	
			messages.warning(request, "Impossible de répondre à votre demande")	
			return render(request, self.template_name,{'warning':'Impossible de répondre à votre demande'})
				
#Paymentsuccess view page
class PaymentProcess(TemplateView):
	template_name = "base/payment_success.html"
	def get(self,request):
		return render(request, self.template_name,{'success':"Monthly subscription successfully done!"})

class SavePayment(TemplateView):
	def post(self,request):
		response = {}
		sub = Subscription.objects.create(offer_id=request.POST.get('os0'),payment_method=request.POST.get('payment_method'), purchaser_id=request.user.id, company_name=request.POST.get('campany_name'),manager_name=request.POST.get('manager_name'), email=request.POST.get('email'), contact_number=request.POST.get('phone'),country=request.POST.get('country'))
		response['payment_id']= sub.id
		return HttpResponse(json.dumps(response),content_type='application/json',status=200)

#PaymentProcess
class Paymentsuccess(TemplateView):
	template_name = "base/payment_success.html"
	def post(self,request,*args, **kwargs):
		payer_status = request.POST.get('payer_status')
		if (payer_status == 'verified'):
			exp_date = datetime.datetime.now()+datetime.timedelta(+30)
			order_id = request.POST.get('custom');
			sub = Subscription.objects.filter(id=order_id)
			complete = sub.update(status=True, expiry_date=exp_date,purchased_at=datetime.datetime.now())
			if(complete):
				return render(request, self.template_name,{'msg':'Paymant fait avec succès'})
		else:
			render(request, self.template_name,{'msg':'Impossible de répondre à votre demande'})		
		return render(request, self.template_name,{'msg':'Impossible de répondre à votre demande'})	

class Deactivate(TemplateView):
	def get(self,request):
		curr = datetime.date.today()
		expiry_date = curr + relativedelta(months=21)
		unsub = UserProfile.objects.filter(user_id=request.user.id)
		comp = unsub.update(subscription=False, expiry_date=expiry_date,deactivate=True)
		if(comp):
			messages.success(request, "Abonnement désactivé avec succès")
			return redirect('my_dashboard')
		messages.warning(request, "Impossible de répondre à votre demande")	
		return redirect('my_dashboard')

class Reactivate(TemplateView):	
	def get(self,request):
		curr = datetime.date.today()
		reactivate = UserProfile.objects.filter(user_id=request.user.id)
		comp = reactivate.update(subscription=True, expiry_date=curr,deactivate=False)
		if(comp):
			messages.success(request, "Abonnement réactivé avec succès")
			return redirect('my_dashboard')
		messages.warning(request, "Impossible de répondre à votre demande")	
		return redirect('my_dashboard')

class MailAlertView(TemplateView):
	template_name = "base/create_alert.html"
	def get(self, request, *args, **kwargs):
		form = CreateemailalertForm()
		implant_key = CaravaneImplantation.objects.filter(status=True)
		user_type = UserProfile.objects.get_or_none(user_id=request.user.id)
		alerts = Createemailalert.objects.filter(user_id=request.user.id)
		return render(request, self.template_name, {'form':form, 'implant':implant_key, 'user_type':user_type, 'alerts':alerts})

	def post(self, request, *args, **kwargs): 
		form = CreateemailalertForm(request.POST)
		alerts = Createemailalert.objects.filter(user_id=request.user.id)
		if form.is_valid():
			frm = form.save(commit=False)
			frm.user_id = request.user.id
			frm.save()
			messages.success(request, "alerte email créé avec succès")
		else:
			messages.warning(request, "Impossible de répondre à votre demande")
		implant_key = CaravaneImplantation.objects.filter(status=True)
		user_type = UserProfile.objects.get_or_none(user_id=request.user.id)	
		return render(request, self.template_name, {'form':form, 'implant':implant_key, 'user_type':user_type, 'alerts':alerts})		 	

class AlertDelete(TemplateView):
	def get(self, request, pk, *args, **kwargs):
		Delete =Createemailalert.objects.get_or_none(pk=pk).delete()
		messages.success(request, "Alerte E-mail supprimé avec succès!")	
		return redirect('my_email')

class Productfav(TemplateView):
	def get(self, request, slug, *args, **kwargs):
		try:
			product =Product.objects.get_or_none(slug=slug)
			sub = ProductFavorite.objects.create(user_id=request.user.id, product_id=product.id)
			messages.success(request, "Produit ajouté à la liste des favoris")
		except :
			messages.warning(request, "Impossible de répondre à votre demande")
			pass
		return redirect('my_fav_product')
			

class OthersiteView(TemplateView):
	template_name = "base/add_othersite.html"
	def get(self, request, *args, **kwargs):
		form = OthersiteModelForm
		return render(request, self.template_name, {'form':form})

	def post(self, request, *args, **kwargs):
		data = request.POST
		upload = request.FILES
		form = OthersiteModelForm(data, upload)
		if form.is_valid():
			frm = form.save(commit=False)
			frm.user_id = request.user.id
			frm.save()
			messages.success(request, "nouveau site ajouté avec succès")	
		else:
			messages.warning(request, "Impossible de répondre à votre demande")
			return render(request, self.template_name, {'form':form})
		return redirect('othersites')

def get_othersites(request):
	sites1 = OtherSite.objects.filter(status=1, pay_country='Campings en Espagne')
	sites2 = OtherSite.objects.filter(status=1, pay_country='Campings en France')
	sort_form = SortForm(request.GET)
	if request.GET.get('date') == 'desc':
		if request.GET.get('date') == 'desc':
			sites1 = sites1.order_by('-created_at')
			sites2 = sites2.order_by('-created_at')
		elif request.GET.get('date') == 'asc':
			sites1 = sites1.order_by('created_at')
			sites2 = sites2.order_by('created_at')
		if request.GET.get('name') == 'desc':
			sites1 = sites1.order_by('-site_name')
			sites2 = sites2.order_by('-site_name')
		elif request.GET.get('name') == 'asc':
			sites1 = sites1.order_by('site_name')
			sites2 = sites2.order_by('site_name')
	return sites1,sites2, sort_form

class OthersiteList(TemplateView):
	template_name = "base/othersite_list.html"
	def get(self, request, *args, **kwargs):
		try:
			form = SiteForm()
			sites1,sites2, sort_form = get_othersites(request)
		except:
			lists = None
		return render(request, self.template_name, {'sites1':sites1,'sites2':sites2,'sort_form': sort_form})		

class CaravaneContactView(TemplateView):
	def get(self,request,pk):
		user = request.user.id;
		response = {}
		response['status'] =False
		xcontact = CaravaneContact.objects.filter(user =user,destock =pk,status=True).count()
		if xcontact<1:
			CaravaneContact.objects.create(user_id=user,destock_id=pk)
			response['status'] =True 
		else:
			response['status'] ='already contacted' 	
		return HttpResponse(json.dumps(response),content_type='application/json')

class ProductDeleteView(TemplateView):
	def get(self,request,pk):
		try:
			Product.objects.get(pk=pk).delete()
			messages.success(request, "Produit supprimé avec succès")
		except :
			messages.warning(request, "Impossible de répondre à votre demande")
			pass
		return redirect('products')

class ProductCategoryDealerView(TemplateView):
	def get(self, request, user_id):
		template_name = 'base/product_seller.html'
		try:
			product =Product.objects.filter(user=user_id).filter(status=True)
		except:
			product = None	
		return render(request,template_name,{'products':product})	
	

class ProductAccount(TemplateView):
	def get(self,request):
		
		if not request.user.is_authenticated():
			return redirect('un_auth_product')

		user_type = UserProfile.objects.get_or_none(user_id=request.user.id)
		if user_type.user_type==2:
			template_name = 'base/product_account.html'
			return render(request,template_name)
		else:
			return redirect('boutique')
			
class DestockAccount(TemplateView):
	def get(self,request):
		if not request.user.is_authenticated():
			return redirect('un_auth_destock')

		user_type = UserProfile.objects.get_or_none(user_id=request.user.id)	
		if user_type.user_type==1:
			template_name = 'base/destock_account.html'
			return render(request,template_name)
		else:
			return redirect('my_destock')


class Phplistsub(TemplateView):
	def post(self, request):
		if(request.POST):
			query = Query().from_table('phplist_user_user').where(email = request.POST.get('email'))
			userEx = query.select()
			if(userEx):
				messages.warning(request, "user already subscribed!")
				return redirect('my_dashboard')
			else:	
				query = Query().from_table(table='phplist_user_user',fields=['email','confirmed','htmlemail'])
				rows = [[request.POST.get('email'), 1, 1]]
				query.insert(rows)
				query = Query().from_table('phplist_user_user').where(email = request.POST.get('email'))
				userEx = query.select()
				user_type = UserProfile.objects.get_or_none(user_id=request.user.id)
				user_type.phplist=1
				user_type.phplist_id=int(userEx[0]['id'])
				user_type.save()
				messages.success(request, "l'utilisateur a souscrit avec succès")
				return redirect('my_dashboard')
		return redirect('my_dashboard')        

class Phplistunsub(TemplateView):
	def post(self, request):
		cursor = connection.cursor()	
		if(request.POST):
			phplist_id = request.POST.get('phplist_id')
			cursor.execute("DELETE FROM phplist_user_user WHERE id="+phplist_id)
			transaction.set_dirty()        
			transaction.commit()
			user_type = UserProfile.objects.get_or_none(user_id=request.user.id)
			user_type.phplist=0
			user_type.save()
			messages.success(request, "désabonné utilisateur avec succès")
			return redirect('my_dashboard')

class HistoryView(TemplateView):
	template_name = 'base/history.html'
	def get(self, request, *args, **kwargs):
		form = HistorySearchForm()
		currentYear = datetime.datetime.now().year
		year = request.GET.get('year')
		history = None
		if year:
			form = HistorySearchForm(request.GET)
			try:
				history = History.objects.filter(status=True,event_date__year=year)
			except:
				history = None
		else:		
			try:
				history = History.objects.filter(status=True,event_date__year=currentYear)
			except:
				history = None
		return render(request,self.template_name,{'histories':history,'form':form})

#product Activation and deactivation
class ProductAcivateView(TemplateView):
	def get(self, request, product_id):
		try:
			product = Product.objects.get_or_none(id=product_id)
			product.status=1
			product.save()
			messages.success(request, "produit activé avec succès")
		except:
			messages.warning(request, "Impossible de répondre à votre demande")
			pass
		return redirect('my_shop')

class ProductDeactivateView(TemplateView):
	def get(self, request, product_id):
		try:
			product = Product.objects.get_or_none(id=product_id)
			product.status=0
			product.save()
			messages.success(request, "produit désactivé avec succès")
		except:
			messages.warning(request, "Impossible de répondre à votre demande")
			pass
		return redirect('my_shop')		

#destock activate deactivate
class DestockAcivateView(TemplateView):
	def get(self, request, destock_id):
		try:
			destock = Destocking.objects.get_or_none(id=destock_id)
			destock.status=1
			destock.save()
			messages.success(request, "Déstockage caravane activé avec succès")
		except:
			messages.warning(request, "Impossible de répondre à votre demande")
			pass
		return redirect('my_destock_list')

class DestockDeactivateView(TemplateView):
	def get(self, request, destock_id):
		try:
			destock = Destocking.objects.get_or_none(id=destock_id)
			destock.status=0
			destock.save()
			messages.success(request, "Déstockage caravane désactivé avec succès")
		except:
			messages.warning(request, "Impossible de répondre à votre demande")
			pass
		return redirect('my_destock_list')	

class PartnersPage(TemplateView):
	template_name = 'base/partner.html'
	def get(self, request, *args, **kwargs):
		partners = Partners.objects.filter(status=True).order_by('title')
		partners_a_to_c = partners.filter(Q(title__istartswith='a')| Q(title__istartswith='b')|Q(title__istartswith='c'))
		partners_d_to_h = partners.filter(Q(title__istartswith='d')| Q(title__istartswith='e')|Q(title__istartswith='f')|Q(title__istartswith='g')|Q(title__istartswith='h'))
		partners_i_to_m = partners.filter(Q(title__istartswith='i')| Q(title__istartswith='j')|Q(title__istartswith='k')|Q(title__istartswith='l')|Q(title__istartswith='m'))
		partners_n_to_t = partners.filter(Q(title__istartswith='n')| Q(title__istartswith='o')|Q(title__istartswith='p')|Q(title__istartswith='q')|Q(title__istartswith='r')|Q(title__istartswith='s')|Q(title__istartswith='t'))
		partners_u_to_z = partners.filter(Q(title__istartswith='u')| Q(title__istartswith='v')|Q(title__istartswith='w')|Q(title__istartswith='x')|Q(title__istartswith='y')|Q(title__istartswith='z'))
		return render(request,self.template_name,{'partners_a_to_c':partners_a_to_c,'partners_d_to_h':partners_d_to_h,'partners_i_to_m':partners_i_to_m,'partners_n_to_t':partners_n_to_t,'partners_u_to_z':partners_u_to_z})

class SitemapView(TemplateView):
	template_name = 'base/site_map.html'
	def get(self, request, *args, **kwargs):
		sitemap = {}
		footers = Menu.objects.get_or_none(name='footer')
		videos =VideoCategory.objects.filter(status=True).order_by('orderby')
		node = ClassifiedCategory.objects.filter(status=True).order_by('sort','tree_id')
		product =ProductCategory.objects.filter(status=True).order_by('name')
		document = Document.objects.filter(status=True).order_by('name')
		if footers is not None:
			footers = footers.menuitem_set
		sitemap = {
			'footers':footers,
			'videos':videos,
			'nodes':node,
			'product':product,
			'document':document
		}	
		return render(request,self.template_name,{'sitemap':sitemap})

class StatisticDetailView(TemplateView):
	template_name = 'base/statistic_details.html'

	def get(self, request, slug):
		try:
			statics = Statistic.objects.get(slug=slug)
		except:
			statics = None
		
		return render(request, self.template_name, { 'statics':statics})

class NewscDetailView(TemplateView):
	template_name = 'base/news_details.html'

	def get(self, request, slug):
		try:
			news = Newspaper.objects.get(slug=slug)
		except:
			news = None
		return render(request, self.template_name, { 'news':news})

class Userupdatemember(TemplateView):
	def get(self, request):
		response = {}
		response['success'] = "success";
		members = Membre.objects.all()
		for value in members:
			existuser = User.objects.filter(Q(username=value.login) | Q(email=value.email))
			if(existuser):
				pass
			else:
				user = get_user_model().objects.create(username = value.login, first_name=value.prenom, email=value.email, last_name=value.nom, is_active=True, date_joined= value.inscription)
				user.set_password(value.password)
				user.save()
				profile = UserProfile.objects.create(user_id=user.id,first_name= user.first_name,last_name =user.last_name,user_type=1 )
				profile.save()
		return HttpResponse(json.dumps(response),content_type='application/json')

class Userupdateclassified(TemplateView):
	def get(self, request):
		classified = Externalclassified.objects.filter(type=1)
		for clas in classified:
			user = Membre.objects.filter(id=clas.id_membre)
			cat = Externalcategorie.objects.filter(id=clas.id_cat)
			cuser = User.objects.filter(username=user[0].login)
			if cuser:
				ccat = ClassifiedCategory.objects.filter(description=cat[0].nom,parent_id=69)
				if ccat:
					add = Classified()	
					add.user_id=int(cuser[0].id)
					add.category_id=1
					add.sub_category_id=int(ccat[0].id)
					add.title=clas.titre
					add.description=clas.description
					add.slug=clas.titre
					add.country='FR'
					add.save()
		response = {}
		response['success'] = 'success classifieds updated'		
		return HttpResponse(json.dumps(response),content_type='application/json')
			
	#update user profile
class AutoUpdateprofile(TemplateView):
	def get(self, request):
		cursor = connection.cursor()
		datas = ['2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','19','21','22','23','25','27','28','29','32','33','34','36','37','38','43','54']
		for data in datas:
			profile = UserProfile.objects.create(user_id=data)

		transaction.set_dirty()        
		transaction.commit()
		response = {}
		response['success'] = 'success updated'		
		return HttpResponse(json.dumps(response),content_type='application/json')

class Setnewpassword(TemplateView):
	def randomword(self, length):
		return ''.join(random.choice(string.lowercase) for i in range(length))

	def post(self, request):
		user = None	
		email = request.POST.get('reset-forum-email')
		password = self.randomword(10)
		url = settings.SITE_URL+'/forum/gen_password.php'
		#url  = 'http://localhost:8888/forum/gen_password.php'
		info = {}
		info['password']= password

		#initial Check with django 
		try:
			user = User.objects.get(username=email)
			user.set_password(password)
			user.save()
		except:
			sql = '''SELECT * FROM bb3_users where username= '%s\'''' %(email)
			cursor = connection.cursor()
			cursor.execute(sql)	
			row = cursor.fetchone()
			row = list(row)
			if row:
				user = get_user_model().objects.create(username = row[7], email=row[12], is_active=True)
				user.set_password(password)
				user.save()
				profile = UserProfile.objects.create(user_id=user.id)
				profile.forumpassword = password
				profile.save()
			else:
				user = None		
		try:
			profile = UserProfile.objects.get(user_id=user.id)
			profile.forumpassword = password
			profile.save()
		except:
			pass

		#initial Check with django 	
		if user:
			details = {'password':password, 'email': user.email}
			r = requests.post(url, params=details)
			data = json.loads(r.text)
			mail_id = user.email
			subject = 'Nouveau mot de passe fixe avec succès'
			sender = 'support@lacaravane.com'
			send_html_email(subject,sender,mail_id,'mail/set-password.html',{ 'data':info})
			messages.success(request, "nouveau mot de passe fixe avec succès")
			return render(request, 'base/home.html')
		else:	
			messages.warning(request, "Impossible de répondre à votre demande")
			return render(request, 'base/home.html')



class StatisticView(TemplateView):
	template_name = "base/statistic.html"
	def get(self, request):
		statistics = {}
		stat_1999 = Statistic.objects.filter(date__year =1999).order_by('month')
		stat_2000 = Statistic.objects.filter(date__year =2000).order_by('month')
		stat_2001 = Statistic.objects.filter(date__year =2001).order_by('month')
		stat_2002 = Statistic.objects.filter(date__year =2002).order_by('month')
		stat_2003 = Statistic.objects.filter(date__year =2003).order_by('month')
		stat_2004 = Statistic.objects.filter(date__year =2004).order_by('month')
		stat_2006 = Statistic.objects.filter(date__year =2006).order_by('month')
		stat_2007 = Statistic.objects.filter(date__year =2007).order_by('month')
		stat_2008 = Statistic.objects.filter(date__year =2008).order_by('month')
		stat_2009 = Statistic.objects.filter(date__year =2009).order_by('month')
		stat_2010 = Statistic.objects.filter(date__year =2010).order_by('month')
		stat_2011 = Statistic.objects.filter(date__year =2011).order_by('month')
		stat_2012 = Statistic.objects.filter(date__year =2012).order_by('month')
		stat_2013 = Statistic.objects.filter(date__year =2013).order_by('month')
		stat_2014 = Statistic.objects.filter(date__year =2014).order_by('month')
		stat_2015 = Statistic.objects.filter(date__year =2015).order_by('month')

		stats = Statistic.objects.filter(year__gte=2004).annotate(dcount=Count('year'))
		statistics = {
			'stat_1999':stat_1999,
			'stat_2000':stat_2000,
			'stat_2001':stat_2001,
			'stat_2002':stat_2002,
			'stat_2003':stat_2003,
			'stat_2004':stat_2004,	
			'stat_2006':stat_2006,
			'stat_2007':stat_2007,
			'stat_2008':stat_2008,
			'stat_2009':stat_2009,
			'stat_2010':stat_2010,
			'stat_2011':stat_2011,
			'stat_2012':stat_2012,
			'stat_2013':stat_2013,
			'stat_2014':stat_2014,
			'stat_2015':stat_2015,
			'stats':stats,
		}
		return render(request,self.template_name,{'statistics':statistics})

