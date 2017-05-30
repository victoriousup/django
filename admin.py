from django.contrib import admin
from lacaravane.models import Siteinfo,Slider,Menu,MenuItem,Page,Advertisement,Document,DocumentItem,ChoiceKey,ChoiceOption,Caravane,Video,Site,VideoCategory,Country,State,Meeting,MeetingImage,MeetingLink,MeetingRegistrationForm,ClassifiedCategory,ClassifiedDepartment,Classified,ClassifiedFavorite,ClassifiedImage,CaravaneImplantation,CaravaneBrand,CaravaneRegYear,ClassifiedPriceRange,MeetingOffer,MeetingActivities,UserCountry,UserTownship,ProductCategory,Product,TemplateUpload,Position,BannerImage,ClassifiedRegion,Destocking,UserProfile,Offer,OtherSite,Subscription,Newspaper,History,Partners,StatisticPage,Statistic
from django_mptt_admin.admin import DjangoMpttAdmin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.db.models import signals
#mail function
from django.template.loader import render_to_string
from django.utils.html  import strip_tags
from django.core.mail import EmailMultiAlternatives  
from django.dispatch import receiver
#tree view
from mptt.admin import MPTTModelAdmin

from models import Banishment, Whitelist

class DocumentItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'status']
    ordering = ["status"]

class CaravaneAdmin(admin.ModelAdmin):
    list_display = ['user', 'status']
    readonly_fields = ('slug',)

class SiteAdmin(admin.ModelAdmin):
    list_display = ['user', 'site_name', 'site_url', 'status']

class VideoAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'status', 'remove']
    
class MenuItemAdmin(admin.ModelAdmin):
	list_display = ['menu', 'page', 'name']

class VideoCategoryAdmin(admin.ModelAdmin):
	list_display = ['category_name']	

class DocumentAdmin(admin.ModelAdmin):
	list_display = ['name', 'status']
	readonly_fields = ("slug",)

class MeetingAdmin(admin.ModelAdmin):
    list_display = ['title']
    readonly_fields = ('slug',)
    
class MeetingRegistrationFormAdmin(admin.ModelAdmin):
    list_display = ['user']

class ClassifiedAdmin(admin.ModelAdmin):
    list_filter = ['status', ]
    list_display = ['title']
    readonly_fields = ('slug',) 

class ClassifiedCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    readonly_fields = ('slug',)
    ordering = ["-sort"]

class ClassifiedDepartmentAdmin(admin.ModelAdmin):
    list_display = ['name']
    readonly_fields = ('slug',)

class ClassifiedImageAdmin(admin.ModelAdmin):
    list_display = ['image']

class CustomMPTTModelAdmin(MPTTModelAdmin): 
    mptt_level_indent = 25
    readonly_fields = ('slug',) 
class ClassifiedPriceRangeAdmin(admin.ModelAdmin):
     list_display = ['title']  

class MeetingOfferAdmin(admin.ModelAdmin):
    list_display = ['title']              

class MeetingActivitiesAdmin(admin.ModelAdmin):
    list_display = ['title'] 

class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    readonly_fields = ("slug",)  

class ProductAdmin(admin.ModelAdmin):
    list_filter = ['status', ]
    list_display = ['name','status']
    readonly_fields = ("slug",)

class PositionAdmin(admin.ModelAdmin):
    list_display = ['position']

class BannerImageAdmin(admin.ModelAdmin):
    list_display = ['image'] 

class ClassifiedRegionAdmin(admin.ModelAdmin):
    list_display = ['name']
    readonly_fields = ("slug",)

class UserProfileAdmin(admin.ModelAdmin):
    list_filter = ['user_type', ]
    list_display = ['user','first_name','last_name','user_type'] 
    sortable_field_name = "user_type"

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['company_name','manager_name'] 

class NewspaperAdmin(admin.ModelAdmin):
    list_display = ['title']  

class HistoryAdmin(admin.ModelAdmin): 
    list_display=['work']

class PartnersAdmin(admin.ModelAdmin): 
    list_display=['title']

class StatisticPageAdmin(admin.ModelAdmin): 
    list_display=['title']

class StatisticAdmin(admin.ModelAdmin):
    list_display = ['title']
    readonly_fields = ("slug",)
class DestockingAdmin(admin.ModelAdmin):
    list_filter = ['status',]
    list_display = ['model','status']

class TemplateUploadAdmin(admin.ModelAdmin):
    list_filter = ['caravane',]
    list_display = ['caravane','template']

class SiteinfoAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

admin.site.register(Siteinfo,SiteinfoAdmin)
admin.site.register(Slider)
admin.site.register(Menu)
admin.site.register(Advertisement)
admin.site.register(Document,DocumentAdmin)
admin.site.register(DocumentItem, DocumentItemAdmin)
admin.site.register(ChoiceKey)
admin.site.register(ChoiceOption)
admin.site.register(Caravane, CaravaneAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(Site, SiteAdmin)
admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(Page)
admin.site.register(VideoCategory,VideoCategoryAdmin)
admin.site.register(Meeting,MeetingAdmin)
admin.site.register(MeetingImage)
admin.site.register(MeetingLink)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(MeetingRegistrationForm,MeetingRegistrationFormAdmin)
admin.site.register(ClassifiedDepartment,ClassifiedDepartmentAdmin)
admin.site.register(Classified,ClassifiedAdmin)
admin.site.register(ClassifiedImage,ClassifiedImageAdmin)
admin.site.register(ClassifiedFavorite) 
admin.site.register(ClassifiedCategory, CustomMPTTModelAdmin)
admin.site.register(CaravaneImplantation) 
admin.site.register(CaravaneBrand) 
admin.site.register(CaravaneRegYear)
admin.site.register(UserCountry)  
admin.site.register(UserTownship) 
admin.site.register(ClassifiedPriceRange, ClassifiedPriceRangeAdmin)
admin.site.register(MeetingOffer, MeetingOfferAdmin)
admin.site.register(MeetingActivities, MeetingActivitiesAdmin)
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(BannerImage, BannerImageAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ClassifiedRegion,ClassifiedRegionAdmin)
admin.site.register(TemplateUpload, TemplateUploadAdmin)
admin.site.register(Destocking,DestockingAdmin)
admin.site.register(UserProfile,UserProfileAdmin)
admin.site.register(Offer)
admin.site.register(OtherSite)
admin.site.register(Subscription,SubscriptionAdmin)
admin.site.register(Newspaper,NewspaperAdmin)
admin.site.register(History,HistoryAdmin)
admin.site.register(Partners,PartnersAdmin)
admin.site.register(StatisticPage,StatisticPageAdmin)
admin.site.register(Statistic,StatisticAdmin)
admin.site.register(Banishment)
admin.site.register(Whitelist)