from django_filters import FilterSet,RangeFilter
from lacaravane.models import Caravane, Classified, Destocking,Createemailalert

class CaravaneFilter(FilterSet):
	class Meta:
		model = Caravane
		fields = ['caravane_type', 'brand','implantation_caravane','total_weight','external_width_of_box','number_of_seats']

class ClassifiedFilter(FilterSet):
	class Meta:
		model = Classified
		# fields = ['title','category', 'department','location','price']
		fields = {'title': ['exact'],'category': ['exact'],'department': ['exact'],'location': ['exact'],'price': ['lt', 'gt'],'country': ['exact']}

class DestockFilter(FilterSet):
	class Meta:
		model = Destocking
		fields = {'caravane_type': ['exact'],'brand': ['exact'],'implantation': ['exact'],'price': ['lt', 'gt'],'country': ['exact']}

class AlertFilter(FilterSet):
	class Meta:
		model = Createemailalert
		fields = {'caravane_type': ['exact'], 'brand': ['exact'], 'implantation': ['exact'], 'country': ['exact'], 'price': ['lt', 'gt']}	