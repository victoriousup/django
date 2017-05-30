from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse
import datetime
from lacaravane.models import Document,DocumentItem,Caravane,Video,VideoComment,Site,ContactUs,VideoCategory,MeetingRegistrationForm,ClassifiedFavorite,ClassifiedCategory,ClassifiedDepartment,Classified,ClassifiedAbuse,CaravaneImplantation,CaravaneRegYear,CaravaneBrand,ClassifiedPriceRange,UserCountry,UserTownship,UserProfile,Product,ProductCategory,ProductAbuse,Destocking,DestockingImage,DestockingFavorite,Offer,Createemailalert,OtherSite,Subscription,Meeting


class MainSitemap(Sitemap):
    changefreq = "daily"
    priority = 1

    def items(self):
        return ['home', 'documents','doc1','doc2','doc3','doc4','caravans_model','caravans_list','add_template','site_list','contact_us','meeting','previous_meeting','classified','new_classified','view_destock','my_destock','my_destock_list','my_fav_destock',
        'add_othersite','othersites','my_fav_product','my_dashboard','my_document','my_caravane','my_meeting','my_classified','myfav_classified','my_video','my_site','my_shop','my_email','forum_view','chat_view','geolocal','geolocal_france','products','add_product','product_home','destock_home','my_dealer_dashboard','history','partner']

    def location(self, item):
        return reverse(item) 

class DocumentSitemap(Sitemap):
    changefreq = "daily"
    priority =1
    def items(self):
        return Document.objects.all()

class VideoSitemap(Sitemap):
    changefreq = "daily"
    priority =1
    def items(self):
        return VideoCategory.objects.all()

class MeetingSitemap(Sitemap):
    changefreq = "daily"
    priority =1
    def items(self):
        return Meeting.objects.all()
    def lastmod(self, obj):
        return obj.created_at.date()     

class ClassifiedCategorySitemap(Sitemap):
    changefreq = "daily"
    priority =1
    def items(self):
        return ClassifiedCategory.objects.all()
    def lastmod(self, obj):
        return obj.created_at.date()

class ClassifiedSitemap(Sitemap):
    changefreq = "daily"
    priority =1
    def items(self):
        return Classified.objects.all()
    def lastmod(self, obj):
        return obj.created_at.date() 

class ProductCategorySitemap(Sitemap):
    changefreq = "daily"
    priority =1
    def items(self):
        return ProductCategory.objects.all()

class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority =1
    def items(self):
        return Product.objects.all()
    def lastmod(self, obj):
        return obj.created_at.date() 

class DestockingSitemap(Sitemap):
    changefreq = "daily"
    priority =1
    def items(self):
        return Destocking.objects.all()
    def lastmod(self, obj):
        return obj.created_at.date()                             


