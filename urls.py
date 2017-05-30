""" Default urlconf for lacaravane """
from django.conf.urls import include, patterns, url
from django.contrib import admin
from django.conf import settings
from lacaravane.views import password_reset,documents,CaravanView,CaravanList,AddTemplate,template_upload,SiteList,contact_us,ViewForumPage,ViewChatPage,StaticPages,classified_imag,videoMyView,SiteMyView,CheckLogin,destock_imag,PaymentCancelled,ViewForumFrPage,ViewForumAuPage, site_custom_view
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from .views import CaravansModelView,VideoList,VideoCategoryList,ForumPage,MeetingsPage,Meetingview,ClassifiedWithCategory,Classifiedview,ClassifiedModelView,ClassifiedDetails,DocumentMyView,MyAccountDashboard,CaravaneMyView,ClassifiedSearch,MeetingMyView,ClassisfiedMyView,MeetingPartnerOfferview,MeetingRegisterview,MeetingActivitesview,Geolocalview,GeolocalFranceview,ProductView,ProductCategoryView,ProductModelView,ProductDetailView,ProductMyView,ClassifiedDelete,ClassifiedEdit,ClassifiedCategoryView,PreviousMeetingsPage,ClassisfiedMyFavorites,GetDeptView,DestockModelView,DestockView,DestockDetails,DestockMyView,DestockMyFavView,MysalesArea,Paymentsuccess,SavePayment,PaymentProcess,Deactivate,Reactivate,MailAlertView,AlertDelete,Productfav,ProductMyFavView,OthersiteView,OthersiteList,DestockMyListView,CaravaneContactView,DestockAccountview,ProductDeleteView,ProductCategoryDealerView,ProductAccount,DestockAccount,Phplistsub,Phplistunsub,MyAccountDealerDashboard,HistoryView,PartnersPage,SitemapView,BoutiqueMyView,BoutiqueAccountview,MyAccountBoutiqueDashboard,StatisticView,StatisticDetailView,ProductAcivateView,ProductDeactivateView,DestockAcivateView,DestockDeactivateView,DestockAccountBlock,DestockUnauth,BoutiqueUnauth,ProductAccountBlock,NewscDetailView,Userupdatemember, Userupdateclassified, AutoUpdateprofile, Setnewpassword

admin.autodiscover()

from django.views.decorators.csrf import csrf_exempt
from django.contrib.sitemaps import FlatPageSitemap, GenericSitemap 
from django.contrib.sitemaps.views import sitemap
from lacaravane.sitemaps import MainSitemap,DocumentSitemap,VideoSitemap,MeetingSitemap,ClassifiedCategorySitemap,ClassifiedSitemap,ProductCategorySitemap,ProductSitemap,DestockingSitemap

def bad(request):
    """ Simulates a server error """
    1 / 0

sitemaps = {
    'static': MainSitemap,
    'document':DocumentSitemap,
    'video':VideoSitemap,
    'meeting':MeetingSitemap,
    'classified':ClassifiedCategorySitemap,
    'classdetails':ClassifiedSitemap,
    'product_with_category':ProductCategorySitemap,
    'product_details':ProductSitemap,
    'destocking_details':DestockingSitemap,
}
urlpatterns = patterns('',
    (r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    (r'^admin/',  include(admin.site.urls)), # admin site
    url(r'^bad/$', bad),
    url(r'', include('base.urls')),
    (r'^tinymce/', include('tinymce.urls')),
    (r'^accounts/', include('allauth.urls')),
    (r'^payment/process/', include('paypal.standard.ipn.urls')),
    url(r'^$', TemplateView.as_view(template_name='index.html')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^password/reset/', password_reset, name='la_password_reset'),
    url(r'^documents/(?P<slug>[-\w]+)/$', documents, name='documents'), 
    url(r'^documents', documents, name='documents'),
    


    #(r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap',{'sitemaps': sitemaps, 'template_name':'base/custom_sitemap.html'}),
    url(r'^sitemap.xml$',site_custom_view, name='sitemap'),
)

urlpatterns += patterns('django.views.generic.simple',
    url(r'^redactor/', include('redactor.urls')),
    url(r'^catalogues-de-caravanes', TemplateView.as_view(template_name='catalogues-de-caravanes.html'), name="doc1"),
    url(r'^pour-choisir-sa-caravane', TemplateView.as_view(template_name='pour-choisir-sa-caravane.html'), name="doc2"),
    url(r'^realisations-des-membres', TemplateView.as_view(template_name='realisations-des-membres.html'), name="doc3"),
    url(r'^modes-demploi', TemplateView.as_view(template_name='modes-demploi.html'), name="doc4"),
    url(r'^add-caravan', login_required(CaravansModelView.as_view()), name="caravans_model"),
    url(r'^caravan/(?P<pk>\d+)/$', CaravanView.as_view(), name="caravans_view"),
    url(r'^modeles-caravanes', CaravanList.as_view(), name="caravans_list"),
    url(r'^add-template', AddTemplate.as_view(), name="add_template"),
    url(r'^template-upload', login_required(template_upload), name="template_upload"), 
    url(r'^videos',VideoList.as_view(), name="video_list"),
    url(r'^video/(?P<slug>.+?)/$', VideoCategoryList.as_view(), name="video_view"),
    url(r'^campeurs',SiteList.as_view(), name="site_list"),
    url(r'^contact',contact_us, name="contact_us"),
    url(r'^page/(?P<slugs>.+?)/$', StaticPages.as_view(), name="static_view"),
    url(r'^rencontre',MeetingsPage.as_view(), name="meeting"),
    url(r'^precedentes-rencontres',PreviousMeetingsPage.as_view(), name="previous_meeting"),
    url(r'^view-meeting/(?P<slug>.+?)/$',Meetingview.as_view(), name="meeting_view"),
    url(r'^meeting/(?P<slug>.+?)/partner-offer/$',MeetingPartnerOfferview.as_view(), name="meeting_offer"),
    url(r'^meeting/(?P<slug>.+?)/register/$',MeetingRegisterview.as_view(), name="meeting_register"),
    url(r'^meeting/(?P<slug>.+?)/activities/$',MeetingActivitesview.as_view(), name="meeting_activity"),
    url(r'^annonces',ClassifiedWithCategory.as_view(), name="classified"),
    url(r'^ajax/sub-category/(?P<pk>\d+)/$', ClassifiedCategoryView.as_view(), name="get_subcategory"),
    url(r'^view-classified/(?P<slug>.+?)/$',Classifiedview.as_view(), name="classified_view"),
    url(r'^delete-add/(?P<slug>.+?)/$',ClassifiedDelete.as_view(), name="classified_delete"),
    url(r'^edit-add/(?P<slug>.+?)/$',ClassifiedEdit.as_view(), name="classified_edit"), 
    url(r'^add-classified', login_required(ClassifiedModelView.as_view()), name="new_classified"),
    url(r'^view-classifieds/(?P<slug>[-\w]+)/$',ClassifiedDetails.as_view(), name="view_classified"),
    #destocking
    url(r'^add-destock', login_required(DestockModelView.as_view()), name="new_destock"),
    url(r'^destockage-caravanes-neuves', DestockView.as_view(), name="view_destock"),
    url(r'^destock-details/(?P<pk>\d+)/$',DestockDetails.as_view(), name="destock_details"),
    url(r'^destock-imag-upload', login_required(destock_imag), name="destock_imag_upload"),
    url(r'^mysale-area/', login_required(MysalesArea.as_view()), name="mysales"),
    url(r'^payment/success/$',csrf_exempt(Paymentsuccess.as_view()), name="payment_success"),
    url(r'^payment/cancelled/$',PaymentCancelled, name="payment_faild"),
    # Dealer My book list
    url(r'^accounts/destock/$',DestockMyView.as_view(), name='my_destock'),
    url(r'^accounts/destock-list/$', login_required(DestockMyListView.as_view()), name='my_destock_list'),
    # Favorites destocking list
    url(r'^accounts/fav-destock/$', login_required(DestockMyFavView.as_view()), name='my_fav_destock'),
    #fav Products



    #othersite
    url(r'^add-site/$', login_required(OthersiteView.as_view()), name='add_othersite'),
    url(r'^campings-partenaires/$', OthersiteList.as_view(), name='othersites'),
    url(r'^accounts/fav-product/$', login_required(ProductMyFavView.as_view()), name='my_fav_product'),
    url(r'^unsubscripe/$',login_required(Deactivate.as_view()), name='deactivate_sub'),
    url(r'^reactivate/$',login_required(Reactivate.as_view()), name='reactivate_sub'),
    url(r'^classified',ClassifiedSearch.as_view(), name="classified_search"),
    url(r'^imag-upload', login_required(classified_imag), name="class_imag_upload"),
    url(r'^accounts/dashboard', login_required(MyAccountDashboard.as_view()), name='my_dashboard'),
    url(r'^accounts/document/$', login_required(DocumentMyView.as_view()), name='my_document'),
    url(r'^accounts/caravane/$', login_required(CaravaneMyView.as_view()), name='my_caravane'),
    url(r'^accounts/meeting/$', login_required(MeetingMyView.as_view()), name='my_meeting'),
    url(r'^accounts/classified/$', login_required(ClassisfiedMyView.as_view()), name='my_classified'),
    url(r'^accounts/favorites/$', login_required(ClassisfiedMyFavorites.as_view()), name='myfav_classified'),
    url(r'^accounts/video/$', login_required(videoMyView.as_view()), name='my_video'),
    url(r'^accounts/site/$', login_required(SiteMyView.as_view()), name='my_site'),
    url(r'^accounts/shop/$', login_required(ProductMyView.as_view()), name='my_shop'),
    url(r'^accounts/create-mail/$', login_required(MailAlertView.as_view()), name='my_email'),
    url(r'^delete-alert/(?P<pk>\d+)/$',login_required(AlertDelete.as_view()), name="alert_delete"), 
    url(r'^forums', ViewForumPage, name='forum_view'),
    url(r'^campings-autres-pays', ViewForumAuPage, name='forum_view_autre'),
    url(r'^campings-france', ViewForumFrPage, name='forum_view_fr'),
    url(r'^mini-chat', ViewChatPage, name='chat_view'),
    url(r'^check-login/$', csrf_exempt(CheckLogin.as_view()), name='check_login'),
    url(r'^geolocalisation-membres',Geolocalview.as_view(), name="geolocal"),
    url(r'^geolocalisation-membres-france',GeolocalFranceview.as_view(), name="geolocal_france"),
    url(r'^boutique',ProductView.as_view(), name="products"),
    url(r'^product/(?P<slug>[-\w]+)/$',ProductCategoryView.as_view(), name="product"),
    url(r'^add-product/$',login_required(ProductModelView.as_view()), name="add_product"),
    url(r'^view-product/(?P<slug>[-\w]+)/$',ProductDetailView.as_view(), name="view_product"),
    url(r'^delete-product/(?P<pk>\d+)/$',ProductDeleteView.as_view(), name="delete_product"),
    url(r'^fav-product/(?P<slug>[-\w]+)/$',Productfav.as_view(), name="fav_product"),
    url(r'^ajax/get-departments/(?P<slug>[-\w]+)/$', GetDeptView.as_view(), name="get_dept"),
    url(r'^ajax/contact-caravane/(?P<pk>\d+)/$', CaravaneContactView.as_view(), name="caravane_contact"),
    url(r'^ajax/save-payment/',  csrf_exempt(SavePayment.as_view()), name="sava_payment"),
    url(r'^edit-subscription/(?P<pk>\d+)/$',login_required(DestockAccountview.as_view()), name="account_edit"),
    url(r'^product-dealer/(?P<user_id>\d+)/$',ProductCategoryDealerView.as_view(), name="product_dealer"),
    url(r'^product-home/', ProductAccount.as_view(), name="product_home"),
    url(r'^destock-home/', DestockAccount.as_view(), name="destock_home"), 
    url(r'^block-destock-page/',DestockAccountBlock.as_view(), name="block_destock_page"), 
    url(r'^unauth-destock/',DestockUnauth.as_view(), name="un_auth_destock"), 
    url(r'^unauth-product/',BoutiqueUnauth.as_view(), name="un_auth_product"), 
    url(r'^block-product-page/',ProductAccountBlock.as_view(), name="block_product_page"),

    url(r'^accounts/seller-dashboard', login_required(MyAccountDealerDashboard.as_view()), name='my_dealer_dashboard'),
    url(r'^accounts/boutique-dashboard', login_required(MyAccountBoutiqueDashboard.as_view()), name='my_boutique_dashboard'),
    url(r'^accounts/boutique/', BoutiqueMyView.as_view(), name="boutique"), 
    url(r'^edit-boutique/(?P<pk>\d+)/$',login_required(BoutiqueAccountview.as_view()), name="boutique_edit"),
    #product, desctocking activation and deactivation
    url(r'^product-acivate/(?P<product_id>\d+)/$',login_required(ProductAcivateView.as_view()), name="product_activate"),
    url(r'^product-deacivate/(?P<product_id>\d+)/$',login_required(ProductDeactivateView.as_view()), name="product_deactivate"),

    url(r'^destock-acivate/(?P<destock_id>\d+)/$',login_required(DestockAcivateView.as_view()), name="destock_activate"),
    url(r'^destock-deacivate/(?P<destock_id>\d+)/$',login_required(DestockDeactivateView.as_view()), name="destock_deactivate"),

    #subphplist
    url(r'^phplist-sub/', login_required(Phplistsub.as_view()), name="subphplist"),
    url(r'^phplist-unsub/', login_required(Phplistunsub.as_view()), name="unsubphplist"),
    url(r'^historique-du-site', HistoryView.as_view(), name="history"),


    url(r'^partenaires/', PartnersPage.as_view(), name="partner"),
    url(r'^plan-du-site/', SitemapView.as_view(), name="sitemap"),
    url(r'^statistiques/', StatisticView.as_view(), name="statistic"),
    url(r'^statistic/(?P<slug>.+?)/$', StatisticDetailView.as_view(), name="statistic_view"),
    url(r'^newspaper/(?P<slug>.+?)/$', NewscDetailView.as_view(), name="news_view"),

    url(r'^set-new-password/', Setnewpassword.as_view(), name="setnewpass"),

    # Update data's from extername systems
    url(r'^user-update-member/', Userupdatemember.as_view(), name="memner"),
    url(r'^user-classified-member/', Userupdateclassified.as_view(), name="classified_external"),
     url(r'^update-auto-profile/', AutoUpdateprofile.as_view(), name="update_auto"),


)
urlpatterns += patterns('',
	(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
	'document_root': settings.MEDIA_ROOT}))
