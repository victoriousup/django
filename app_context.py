from django.shortcuts import render, redirect, get_object_or_404
from django.core.cache import cache
from lacaravane.models import Siteinfo,Slider,Menu,Menu_item,Advertisement,DocumentItem,Document,Video,Caravane,Classified,Destocking,MenuItem,Newspaper
from lacaravane.forms import SignupForm,LoginForm,ResetPasswordForm,ResetPasswordKeyForm,ChangePasswordForm,DocumentItemForm

def siteinfo(request):
	data=cache.get('site_info')
	data = None
	try:
		terms_cond = MenuItem.objects.get_or_none(slug='conditions-generales')
	except:
		terms_cond = None
	if data is None:
		siteinfo = Siteinfo.objects.get_or_none(name='lacaravane')
		slider = Slider.objects.filter(status=True)
		footer_menu = Menu.objects.get_or_none(slug='Footer Menu')
		main_menu = Menu.objects.get_or_none(slug='main-menu')
		documents = Document.objects.filter(status=True)
		annonces = Menu.objects.get_or_none(slug='small-ads')
		videos = Video.objects.filter(status=True).order_by('-id')[:3]
		caravanes = Caravane.objects.filter(status=1).order_by('-id')[:3]
		classifieds =  Classified.objects.filter(status=True).order_by('-id')[:8]
		home_right = Advertisement.objects.get_or_none(position='home_right',status=True)
		home_bottom = Advertisement.objects.get_or_none(position='home_bottom',status=True)
		document_top = Advertisement.objects.get_or_none(position='document_top',status=True)
		video_top = Advertisement.objects.get_or_none(position='video_top',status=True)
		caravane_list_top = Advertisement.objects.get_or_none(position='caravane_list_top',status=True)
		caravane_list_detail = Advertisement.objects.get_or_none(position='caravane_list_detail',status=True)
		sites_top = Advertisement.objects.get_or_none(position='sites_top',status=True)
		geolocation_top = Advertisement.objects.get_or_none(position='geolocation_top',status=True)
		meetings_top = Advertisement.objects.get_or_none(position='meetings_top',status=True)
		meetings_detail_top = Advertisement.objects.get_or_none(position='meetings_detail_top',status=True)
		meetings_archived_top = Advertisement.objects.get_or_none(position='meetings_archived_top',status=True)
		meetings_archived_detail_top = Advertisement.objects.get_or_none(position='meetings_archived_detail_top',status=True)
		partners_list_top = Advertisement.objects.get_or_none(position='partners_list_top',status=True)
		classifieds_list_top = Advertisement.objects.get_or_none(position='classifieds_list_top',status=True)
		classifieds_detail_top = Advertisement.objects.get_or_none(position='classifieds_detail_top',status=True)
		destock_list_top = Advertisement.objects.get_or_none(position='destock_list_top',status=True)
		destock_detail_top = Advertisement.objects.get_or_none(position='destock_detail_top',status=True)
		products_list_top = Advertisement.objects.get_or_none(position='products_list_top',status=True)
		products_detail_top = Advertisement.objects.get_or_none(position='products_detail_top',status=True)
		forum_top = Advertisement.objects.get_or_none(position='forum_top',status=True)
		
		destock = Destocking.objects.filter(status=1)[:3]
		papers = Newspaper.objects.filter(status=1)
		# CMS Pages
		footers = Menu.objects.get_or_none(name='footer')
		if footers is not None:
			footers = footers.menuitem_set

		data={
			'output': siteinfo,
			'sliders': slider,
			'footer_menus':footers,
			'main_menus' :main_menu,
			'document' :documents,
			'signup_form': SignupForm(),
			'login_form': LoginForm(),
			'forgot_password':ResetPasswordForm(),
			'reset_password':ResetPasswordKeyForm(),
			'documents':DocumentItemForm(),
			'annonces':annonces,
			'home_right': home_right,
			'home_bottom': home_bottom,
			'document_top': document_top,
			'video_top': video_top,
			'forum_top':forum_top,
			'caravane_list_top': caravane_list_top,
			'caravane_list_detail': caravane_list_detail,
			'sites_top': sites_top,
			'geolocation_top': geolocation_top,
			'meetings_top': meetings_top,
			'meetings_detail_top': meetings_detail_top,
			'meetings_archived_top': meetings_archived_top,
			'meetings_archived_detail_top': meetings_archived_detail_top,
			'partners_list_top': partners_list_top,
			'classifieds_list_top': classifieds_list_top,
			'classifieds_detail_top': classifieds_detail_top,
			'destock_list_top': destock_list_top,
			'destock_detail_top': destock_detail_top,
			'products_list_top': products_list_top,
			'products_detail_top': products_detail_top,
			'videos':videos,
			'caravanes':caravanes,
			'destocks':destock,
			'classifieds':classifieds,
			'terms_cond':terms_cond,
			'paper':papers
			}
	return data

	