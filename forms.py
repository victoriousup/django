# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelForm
import datetime
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _
from allauth.account.forms import SignupForm,LoginForm,ResetPasswordForm,ResetPasswordKeyForm,ChangePasswordForm
from lacaravane.models import Document,DocumentItem,Caravane,ChoiceKey,ChoiceOption,Video,VideoComment,Site,ContactUs,VideoCategory,MeetingRegistrationForm,ClassifiedFavorite,ClassifiedCategory,ClassifiedDepartment,Classified,ClassifiedAbuse,CaravaneImplantation,CaravaneRegYear,CaravaneBrand,ClassifiedPriceRange,UserCountry,UserTownship,UserProfile,Product,ProductCategory,ProductAbuse,Destocking,DestockingImage,DestockingFavorite,Offer,Createemailalert,OtherSite,Subscription
from django.contrib.auth.models import User
from django_countries import countries
from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget

class SignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['username','email','password1','password2','captcha','terms']
    username = forms.CharField(label= "Pseudo",widget=forms.TextInput(attrs={'type': 'text', 'required':'required', 'class': 'form-control', 'placeholder':'Pseudo','data-field':'username','icon':'fa-user'}))
    password1 = forms.CharField(label="Mot de passe", widget=forms.TextInput(attrs={'type': 'password', 'required':'required', 'class': 'form-control', 'placeholder':'Mot de passe' ,'data-field':'password1','icon':'fa-lock'}))
    password2 = forms.CharField(label="Mot de passe",widget=forms.TextInput(attrs={'type': 'password',  'required':'required','class': 'form-control',' placeholder':'Mot de passe','data-field':'password2','icon':'fa-lock'}))
    email =  forms.CharField(label= "Email", widget=forms.TextInput(attrs={'type': 'email', 'placeholder':'Email','class':'form-control','required':'required','data-field':'email','icon':'fa-envelope-o'}))
    captcha = ReCaptchaField(widget=ReCaptchaWidget())
    terms = forms.BooleanField(label="J'accepte les conditions générales d'utilisations de Lacaravane.com",widget=forms.TextInput(attrs={'type': 'checkbox','class':'','required':'required','data-field':'terms'}),required=True)

class LoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['login'].widget = forms.TextInput(attrs={'type': 'text', 'required':'required', 'class': 'form-control', 'placeholder':'Pseudo','data-field':'login','icon':'fa-user'})
        self.fields['password'].widget = forms.TextInput(attrs={'type': 'password', 'required':'required', 'class': 'form-control', 'placeholder':'Mot de passe','data-field':'password','icon':'fa-lock'})
    pass   

class ResetPasswordForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(ResetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget = forms.TextInput(attrs={'type': 'email', 'required':'required', 'class': 'form-control', 'placeholder':'Email','data-field':'email'})
    pass 

class ResetPasswordKeyForm(ResetPasswordKeyForm):
    def __init__(self, *args, **kwargs):
        super(ResetPasswordKeyForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.TextInput(attrs={'type': 'password', 'required':'required', 'class': 'form-control', 'placeholder':'Mot de passe','data-field':'password1'})
        self.fields['password2'].widget = forms.TextInput(attrs={'type': 'password', 'required':'required', 'class': 'form-control', 'placeholder':'Mot de passe','data-field':'password2'})
    pass

class DocumentItemForm(ModelForm):
    LANGUAGE = [
                ("Français","Français"),
                ('Anglais','Anglais'),
                ('Allemand','Allemand'),
                ('Espagnol','Espagnol'),
                ('Italien','Italien'),
                ('Autres','Autres')
            ]
    title = forms.CharField(label='Titre',max_length=200,widget=forms.TextInput(attrs={'type': 'text','class': 'form-control', 'placeholder':'Titre'}))
    description = forms.CharField(label='Description',max_length=300,widget=forms.Textarea(attrs={'type': 'text','class': 'form-control', 'placeholder':'Description - 300 caractères maximum'}))
    pages = forms.IntegerField(label='Pages',widget=forms.TextInput(attrs={'type': 'text','class': 'form-control',' placeholder':'Nombre de pages'}))
    language =  forms.ChoiceField(label='Language',required=True,widget=forms.Select(attrs={'class':'custom-select'}), choices=LANGUAGE)
    photo = forms.ImageField(label='photo',max_length=200,required=True)
    pdf = forms.FileField(label='pdf',max_length=200,required=True)
    document = forms.HiddenInput()

    class Meta:
        model = DocumentItem
    pass


class DocumentItemDocumentsForm(DocumentItemForm):
    documents = Document.objects.all()
    document =  forms.ModelChoiceField(label='Language',required=True,widget=forms.Select(attrs={'class':'custom-select'}), queryset=documents)

class DocumentSortForm(forms.Form):
    ALPHABETS = [
                ('', 'Tri par ordre alphabétique'),
                ('desc', 'Tri par ordre décroissant (Z-A)'),
                ('asc', 'Tri par ordre croissant (A-Z)'),
    ]
    RELEASEDATE = [
                ('', 'Tri par date de parution'),
                ('desc', 'Tri du plus récent au plus ancien'),
                ('asc', 'Tri du plus ancient au plus récent'),
    ]
    date = forms.ChoiceField(label='Alphabetical', required=False, widget=forms.Select(attrs={'class':'custom-select orderby'}), choices=ALPHABETS)
    title = forms.ChoiceField(label='Release', required=False, widget=forms.Select(attrs={'class':'custom-select orderby'}), choices=RELEASEDATE)

class CaravaneModelForm(ModelForm):
    class Meta:
        model = Caravane
        exclude = ('user', 'slug', 'status','internal_dimension','structure_of_caravane')
   
    keys = ChoiceKey.objects
    results = keys.prefetch_related('choices')
    choice_keys = ChoiceKey.objects.all()
    arrange = {}
    data = {}
    implant_key = CaravaneImplantation.objects.filter(status=True)    
    for result in results:
        data[result.choice_key] = result.choices.filter(choice_key_id=result.id)

    # caravane_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    caravane_type = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}),required=True, queryset=data['caravane_type'] if 'caravane_type' in data else None)
    brand = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}),required=True, queryset=data['brand'] if 'brand' in data else None)
    model = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'texte libre < 80 caractères'}),required=True)
    manufacture_year = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}),required=True, queryset=data['manufacture_year'] if 'manufacture_year' in data else None)
    country_registration = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}),required=True, queryset=data['country_registration'] if 'country_registration' in data else None)
    number_of_seats = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}),required=True, queryset=data['number_of_seats'] if 'number_of_seats' in data else None)

    # weight = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    total_weight = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'nombre libre entre 100 et 10000'}),required=True)
    curb_weight = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'nombre libre entre 100 et 10000'}),required=False)
    payload = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'nombre libre entre 100 et 10000'}),required=False)
    weight_in_working_order = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'nombre libre entre 100 et 10000'}),required=False)
    other_payload1 = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}),required=False)
    other_payload2 = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}),required=False)
    other_payload3 = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}),required=False)
    other_payload4 = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}),required=False)

    # external_dimension = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    boom_length = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'nombre libre (entre 50 et 20000)'}),required=False)
    external_length_of_box = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre libre (entre 50 et 20000)'}),required=False)
    external_width_of_box = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre libre (entre 50 et 20000)'}),required=False)
    external_height_of_caravane = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre libre (entre 50 et 20000)'}),required=False)
    external_height_of_folded_catavane = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre libre (entre 50 et 20000)'}),required=False)
    external_developed_awning = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre libre (entre 300 et 20000)'}),required=False)

    # internal_dimension = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    internal_length_of_box = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre libre (entre 50 et 20000)'}),required=False)
    internal_width_of_box = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre libre (entre 50 et 20000)'}),required=False)
    # internal_height_of_caravane = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre libre (entre 50 et 20000)'}))
    # internal_height_of_folded_catavane = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre libre (entre 50 et 20000)'}))
    # bed_type_size = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    before_caravane_type = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}),required=False, queryset=data['before_caravane_type'] if 'before_caravane_type' in data else None)
    before_caravane_size = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'texte libre < 80 caractères'}),required=False,)
    middle_caravane_type = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}),required=False, queryset=data['middle_caravane_type'] if 'middle_caravane_type' in data else None)
    middle_caravane_size = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'texte libre < 80 caractères'}),required=False,)
    back_caravane_type = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}),required=False, queryset=data['back_caravane_type'] if 'back_caravane_type' in data else None)
    back_caravane_size = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'texte libre < 80 caractères'}),required=False)

    drinking_water_tank = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}),required=False, queryset=data['drinking_water_tank'] if 'drinking_water_tank' in data else None)
    drinking_water_capacity = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre libre (entre 1 et 1000)'}),required=False)
    waste_water_tank = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}),required=False, queryset=data['waste_water_tank'] if 'waste_water_tank' in data else None)
    waste_water_capacity = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre libre (entre 1 et 1000)'}),required=False)
    battery = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}),required=False, queryset=data['battery'] if 'battery' in data else None)
    battery_power = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre libre (entre 1 et 1000)'}),required=False)
    solar_panel = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}),required=False, queryset=data['solar_panel'] if 'solar_panel' in data else None)
    solar_power = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre libre (entre 1 et 1000)'}),required=False)
    chemical_toiler = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}),required=False, queryset=data['chemical_toiler'] if 'chemical_toiler' in data else None)
    chemical_type = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}),required=False, queryset=data['chemical_type'] if 'chemical_type' in data else None)
    refrigerator = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}),required=False, queryset=data['refrigerator'] if 'refrigerator' in data else None)


    # refrigerator_type = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}), queryset=data['refrigerator_type'] if 'refrigerator_type' in data else None)

    refrigerator_type = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre libre (entre 1 et 1000)'}),required=False)


    stove = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}),required=False, queryset=data['stove'] if 'stove' in data else None)
    stove_type = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}),required=False, queryset=data['stove_type'] if 'stove_type' in data else None)
    heating = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}), required=False,queryset=data['heating'] if 'heating' in data else None)
    heating_type = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}),required=False, queryset=data['heating_type'] if 'heating_type' in data else None)
    water = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}),required=False, queryset=data['water'] if 'water' in data else None)
    water_type = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre libre (entre 1 et 1000)'}),required=False)
    
    # water_type = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}), queryset=data['water_type'] if 'water_type' in data else None)


    oven = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}),required=False, queryset=data['oven'] if 'oven' in data else None)

    # structure_of_caravane = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    implantation_caravane = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}),required=False, queryset=implant_key)

    structure_dimention = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'texte libre < 80 caractères'}),required=False)
    type_of_chassis = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}),required=False, queryset=data['type_of_chassis'] if 'type_of_chassis' in data else None)
    shocks = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}),required=False, queryset=data['shocks'] if 'shocks' in data else None)
    floor_thickness = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre libre (entre 1 et 1000)'}),required=False)
    wall_thickness = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'nombre libre (entre 1 et 1000)'}),required=False)
    roof_thickness = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre libre (entre 1 et 1000)'}),required=False)
    insulation_type = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'texte libre < 80 caractères'}),required=False)
    cover = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'texte libre < 80 caractères'}),required=False)

    new_purchased_value = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre libre (entre 100 et 500000)'}),required=False)
    current_value = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre libre (entre 100 et 500000)'}),required=False)
    link_our_classified = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'texte libre < 200 caractères'}),required=False)
    list_of_members = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'texte libre < 200 caractères'}),required=False)
    forum_post = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'texte libre < 200 caractères'}),required=False)
    video_url = forms.CharField(max_length=200,widget=forms.TextInput(attrs={'type': 'text','class': 'form-control', 'placeholder':'Tapez l\'adresse du lien de la vidéo'}),required=False)
    # video = forms.FileField()
    templates = forms.HiddenInput()

class CaravaneSearchForm(forms.Form):

    implant_key = CaravaneImplantation.objects.filter(status=True)
    keys = ChoiceKey.objects
    results = keys.prefetch_related('choices')
    choice_keys = ChoiceKey.objects.all()
    arrange = {}
    data = {}
        
    for result in results:
        data[result.choice_key] = result.choices.filter(choice_key_id=result.id)

    caravane_type = forms.ModelChoiceField(widget=forms.Select(attrs={'id': 'caravane_type_custom_selectize'}), queryset=data['caravane_type'] if 'caravane_type' in data else None)
    brand = forms.ModelChoiceField(widget=forms.Select(attrs={'id': 'caravane_brand_custom_selectize'}), queryset=data['brand'] if 'brand' in data else None)
    
    implantation_caravane=forms.ModelChoiceField(widget=forms.Select(attrs={'id': 'implant_custom_selectize'}), queryset=implant_key)
    total_weight = forms.ModelChoiceField(widget=forms.Select(attrs={'id': 'caravane_weight_custom_selectize'}), queryset=data['weight_management'] if 'weight_management' in data else None)
    number_of_seats = forms.ModelChoiceField(widget=forms.Select(attrs={'id': 'caravane_number_custom_selectize'}), queryset=data['number_of_seats'] if 'number_of_seats' in data else None)
    external_width_of_box = forms.ModelChoiceField(widget=forms.Select(attrs={'id': 'caravane_width_custom_selectize'}), queryset=data['width'] if 'width' in data else None)
    option = forms.ModelChoiceField(widget=forms.Select(attrs={'id': 'caravane_option_custom_selectize'}), queryset=data['first_key'] if 'first_key' in data else None)

    # def __init__(self, *args, **kwargs):
    #     super(CaravaneSearchForm, self).__init__(*args, **kwargs)
    #     self.fields['implantation_caravane'].queryset = CaravaneImplantation.objects.filter(status=True)

class VideoModelForm(ModelForm):
    class Meta:
        model = Video

    keys = VideoCategory.objects.filter(status=True)
    video_type_choices=keys
    video_type = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}), queryset=video_type_choices)
    name = forms.CharField(label='Titre',max_length=200,widget=forms.TextInput(attrs={'type': 'text','class': 'form-control', 'placeholder':'Titre'}))
    description = forms.CharField(label='description',max_length=300,widget=forms.Textarea(attrs={'type': 'text','class': 'form-control', 'placeholder':'Description - 300 caractères maximum','rows':'5'}))
    video_url = forms.CharField(label='Titre',max_length=200,widget=forms.TextInput(attrs={'type': 'text','class': 'form-control', 'placeholder':'Tapez l\'adresse du lien de la vidéo'}))
        
class VideoSortForm(forms.Form):
    ALPHABETS = [
                ('', 'Tri par ordre alphabétique'),
                ('desc', 'Tri par ordre décroissant (Z-A)'),
                ('asc', 'Tri par ordre croissant (A-Z)'),
    ]
    RELEASEDATE = [
                ('', 'Tri par date de parution'),
                ('desc', 'Tri du plus récent au plus ancien'),
                ('asc', 'Tri du plus ancient au plus récent'),
    ]
    name = forms.ChoiceField(label='Alphabetical', required=False, widget=forms.Select(attrs={'class':'custom-select filterby'}), choices=ALPHABETS)
    date = forms.ChoiceField(label='Release', required=False, widget=forms.Select(attrs={'class':'custom-select filterby'}), choices=RELEASEDATE)

class SortForm(VideoSortForm):
    pass

class VideoCommentForm(ModelForm):
    class Meta:
        model = VideoComment

    comments = forms.CharField(label='comments',max_length=300,widget=forms.Textarea(attrs={'rows': 5, 'type': 'text','class': 'form-control', 'placeholder':''}))

class SiteForm(ModelForm):
    class Meta:
        model = Site
        exclude = ('user', 'status')
    site_name = forms.CharField(max_length=300,widget=forms.TextInput(attrs={'type': 'text','class': 'form-control', 'placeholder':'Titre de votre site ou blog'}))
    site_url = forms.CharField(max_length=300,widget=forms.TextInput(attrs={'type': 'text','class': 'form-control', 'placeholder':'Adresse URL de votre site ou blog'}))
    description = forms.CharField(max_length=300,widget=forms.Textarea(attrs={'type': 'text','class': 'form-control', 'placeholder':'Description - 300 caractères maximum','rows':'3'}))
    photo = forms.FileField()

class ContactUsForm(ModelForm):
    class Meta:
        model = ContactUs
    first_name = forms.CharField(label='Prénom',max_length=300,widget=forms.TextInput(attrs={'type': 'text','class': 'form-control', 'placeholder':''}))
    last_name = forms.CharField(label='Nom de famille',max_length=300,widget=forms.TextInput(attrs={'type': 'text','class': 'form-control', 'placeholder':''}))
    email = forms.CharField(label='Email',max_length=300,widget=forms.TextInput(attrs={'type': 'text','class': 'form-control', 'placeholder':''}))
    message = forms.CharField(label='Message',max_length=900,widget=forms.Textarea(attrs={'type':'text','class':'form-control','id':'auto-height', 'placeholder':''}))

class ClassifiedFavForm(ModelForm):
    class Meta:
        model = ClassifiedFavorite
        
    user = forms.HiddenInput()
    classified = forms.HiddenInput()

class ClassifiedAbuseForm(ModelForm):
    class Meta:
        model = ClassifiedAbuse
        
    user = forms.HiddenInput()
    classified = forms.HiddenInput()    

class ClassifiedModelForm(ModelForm):
    class Meta:
        model = Classified
    category_keys = ClassifiedCategory.objects.filter(status=True,level=0)
    sub_category_keys = ClassifiedCategory.objects.filter(status=True)
    depart_keys = ClassifiedDepartment.objects.filter()
    brand_key = CaravaneBrand.objects.filter(status=True)
    year_key = CaravaneRegYear.objects.filter(status=True)  
    title = forms.CharField(label='title',max_length=50,widget=forms.TextInput(attrs={'type': 'text','class': 'form-control', 'placeholder':'texte libre < 50 caractères'})) 
    description = forms.CharField(label='comments',max_length=400,widget=forms.Textarea(attrs={'type': 'text','class': 'form-control', 'placeholder':'texte libre < 400 caractères'}))
    category = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize','id':'choose_class_category'}), queryset=category_keys, required=True)
    sub_category = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}), queryset=sub_category_keys, required=False)
    department = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}), queryset=depart_keys, required=False)
    brand = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}), queryset=brand_key, required=False)
    year = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'nombre libre (entre 1900 et 2100)'}), required=True)
    model = forms.CharField(label='model',max_length=50,widget=forms.TextInput(attrs={'type': 'text','class': 'form-control', 'placeholder':'texte libre < 30 caractères'}),required=False)
    price = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre libre (entre 1 et 1000000)'}),required=True)
    location = forms.CharField(label='location',max_length=300,widget=forms.TextInput(attrs={'type': 'text','class': 'form-control classified_location', 'id':'classified_location' }),required=False)
    country = forms.ChoiceField(label=_("Country"),widget=forms.Select(attrs={'id':'class_country_selectize','class': 'class_country_selectize'}),choices=countries,required=True)
    email =  forms.CharField(widget=forms.TextInput(attrs={'type': 'email', 'placeholder':'Mon adresse email','class':'form-control'}),required=True) 
    phone = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class': 'form-control', 'placeholder':'Mon numéro de téléphone'}),required=False) 
    implantation = forms.HiddenInput()
    city = forms.HiddenInput()
    latitude = forms.HiddenInput()
    longitude = forms.HiddenInput()

class DestockModelForm(ModelForm):
    class Meta:
        model=Destocking

    keys = ChoiceKey.objects
    results = keys.prefetch_related('choices')
    choice_keys = ChoiceKey.objects.all()
    data = {}   
    for result in results:
        data[result.choice_key] = result.choices.filter(choice_key_id=result.id)

    brand_key = CaravaneBrand.objects.filter(status=True)
    depart_keys = ClassifiedDepartment.objects.filter()    
    description = forms.CharField(label='comments',max_length=500,widget=forms.Textarea(attrs={'type': 'text','class': 'form-control', 'placeholder':'texte libre < 500 caractères','rows':'4'}))
    country = forms.ChoiceField(label=_("Country"),widget=forms.Select(attrs={'id':'class_country_selectize','class': 'class_country_selectize'}),choices=countries,required=True,initial='FR')
    brand = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}), queryset=brand_key, required=False)
    caravane_type = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}),required=True, queryset=data['caravane_type'] if 'caravane_type' in data else None)
    department = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}), queryset=depart_keys, required=False)
    model = forms.CharField(label='model',max_length=50,widget=forms.TextInput(attrs={'type': 'text','class': 'form-control', 'placeholder':'texte libre < 50 caractères'}),required=False)
    price = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre situé entre 1000 et 200000'}),required=True)
    location = forms.CharField(label='location',max_length=300,widget=forms.TextInput(attrs={'type': 'text','class': 'form-control classified_location', 'id':'classified_location' }),required=False) 
    email =  forms.CharField(widget=forms.TextInput(attrs={'type': 'email', 'placeholder':'Mon adresse email','class':'form-control'}),required=False) 
    phone = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class': 'form-control', 'placeholder':'Mon numéro de téléphone'}),required=False)
    terms = forms.BooleanField(widget=forms.TextInput(attrs={'type': 'checkbox','class':'','required':'required','data-field':'terms'}),required=False)

    weight = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre libre entre 200 et 20000'}),required=True)
    length = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre libre entre 140 et 280'}),required=True)
    inter = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'type': 'text','class': 'form-control', 'placeholder':'texte libre limité à 500 caractères','rows':'4'}))
    exter = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'type': 'text','class': 'form-control', 'placeholder':'texte libre limité à 500 caractères','rows':'4'}))
    year = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'nombre libre entre 2000 à 2050'}),required=True)
    number_of_place = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}),required=True, queryset=data['number_of_seats'] if 'number_of_seats' in data else None)

    implant_image = forms.FileField(required=False)
    dealername = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}),required=False)
    implantation = forms.HiddenInput()
    city = forms.HiddenInput()
    latitude = forms.CharField(widget=forms.TextInput(attrs={'type': 'hidden'}),required=False)
    longitude = forms.CharField(widget=forms.TextInput(attrs={'type': 'hidden'}),required=False)

class DestockSearchForm(forms.Form):
    price_keys = ClassifiedPriceRange.objects.filter()
    implant_key = CaravaneImplantation.objects.filter(status=True) 
    keys = ChoiceKey.objects
    results = keys.prefetch_related('choices')
    choice_keys = ChoiceKey.objects.all()
    arrange = {}
    data = {}    
    for result in results:
        data[result.choice_key] = result.choices.filter(choice_key_id=result.id)
    brand_key = CaravaneBrand.objects.filter(status=True)    
    caravane_type = forms.ModelChoiceField(widget=forms.Select(attrs={'id': 'caravane_type_custom_selectize'}), queryset=data['caravane_type'] if 'caravane_type' in data else None)
    brand = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}), queryset=brand_key, required=False)
    
    implantation=forms.ModelChoiceField(widget=forms.Select(attrs={'id': 'implant_custom_selectize'}), queryset=implant_key)
    price = forms.ModelChoiceField(widget=forms.Select(attrs={'id': 'class_price_selectize'}), queryset=price_keys)
    country = forms.ChoiceField(label='country',widget=forms.Select(attrs={'id':'class_country_selectize','class':'class_country_selectize','placeholder':'pays'}),choices=countries,initial={'country': ''})

class DestockFavForm(ModelForm):
    class Meta:
        model = DestockingFavorite
        
    user = forms.HiddenInput()
    destock = forms.HiddenInput()

class ClassfifiedSearchForm(forms.Form):

    category_keys = ClassifiedCategory.objects.filter(status=True)
    depart_keys = ClassifiedDepartment.objects.filter().order_by('name')
    price_keys = ClassifiedPriceRange.objects.filter()
    title = forms.CharField(label='name',max_length=30,widget=forms.TextInput(attrs={'type': 'text','class': 'form-control','placeholder':' mots-clés'})) 
    category = forms.ModelChoiceField(widget=forms.Select(attrs={'id': 'class_category_selectize'}), queryset=category_keys)
    department = forms.ModelChoiceField(widget=forms.Select(attrs={'id': 'class_dept_selectize'}), queryset=depart_keys)
    price = forms.ModelChoiceField(widget=forms.Select(attrs={'id': 'class_price_selectize'}), queryset=price_keys)
    location = forms.CharField(label='location',max_length=300,widget=forms.TextInput(attrs={'type': 'text','class': 'form-control', 'id':'location_search','placeholder':'Ville' }))
    country = forms.ChoiceField(label='country',widget=forms.Select(attrs={'id':'class_country_selectize','class':'class_country_selectize','placeholder':'pays'}),choices=countries,initial={'country': ''})

class ClassfifiedEmailForm(forms.Form):
    email =  forms.CharField(widget=forms.TextInput(attrs={'type': 'email', 'placeholder':'Email','class':'form-control','required':'required'}))    
    classified = forms.HiddenInput()

class AccountUserFrom(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'location', 'city','country','latitude','longitude']
    first_name = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','required':'required'}),required=True)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','required':'required'}),required=True)
    location = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','id':'user_location'}),required=True)
    city = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','id':'user_city'}),required=True)
    country = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','id':'user_country'}),required=True)
    latitude = forms.CharField(widget=forms.TextInput(attrs={'type': 'hidden','id':'user_latitude'}),required=False)
    longitude = forms.CharField(widget=forms.TextInput(attrs={'type': 'hidden','id':'user_langtitude'}),required=False)
    country_short = forms.CharField(widget=forms.TextInput(attrs={'type': 'hidden','id':'user_country_short'}),required=False)
    political_short = forms.CharField(widget=forms.TextInput(attrs={'type': 'hidden','id':'user_political_short'}),required=False)
    department = forms.CharField(widget=forms.TextInput(attrs={'type': 'hidden','id':'user_department'}),required=False)

class MeetingRegForm(ModelForm):
    class Meta:
        model = MeetingRegistrationForm
    
    keys = ChoiceKey.objects
    results = keys.prefetch_related('choices')
    choice_keys = ChoiceKey.objects.all()
    arrange = {}
    data = {}
        
    for result in results:
        data[result.choice_key] = result.choices.filter(choice_key_id=result.id)

    user = forms.HiddenInput()
    meeting = forms.HiddenInput()
    way_to_come = forms.ModelChoiceField(widget=forms.RadioSelect(attrs={'id':'meeting_way_to'}), queryset=data['way_to_come'] if 'way_to_come' in data else None,initial=0)
    username = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','id':'my-name','class':'form-control input-sm input-width'}),required=False)
    number_of_adult = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize select-width'}), queryset=data['count_number'] if 'count_number' in data else None)
    number_of_child = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize select-width'}), queryset=data['count_number'] if 'count_number' in data else None)
    number_of_animals = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize select-width'}), queryset=data['count_number'] if 'count_number' in data else None)
    name_and_surename = forms.CharField(label='name_and_surename',max_length=400,widget=forms.Textarea(attrs={'type': 'text','rows':'5','class': 'form-control input-sm input-width', 'placeholder':'texte libre < 400 caractères','id':'adult-name'}))
    name_age_child = forms.CharField(label='name_age_child',max_length=400,widget=forms.Textarea(attrs={'type': 'text','rows':'5','class': 'form-control input-sm input-width', 'placeholder':'texte libre < 400 caractères','id':'child-name'}))
    number_street_name = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control input-sm input-width','id':'street-name'}))
    zip_code = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control input-sm input-width','id':'code-postal'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control input-sm input-width','id':'city'}))
    country = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize select-width','id':'country'}), queryset=data['country_registration'] if 'country_registration' in data else None)
    cell_number = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control input-sm input-width','id':'my-num'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control input-sm input-width','id':'my-email'}))
    register = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control input-sm input-width','id':'my-car'}))
    arrival_date = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control input-sm input-width datepicker'})) 
    departure_date = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control input-sm input-width datepicker'})) 
    payment_method = forms.ModelChoiceField(widget=forms.RadioSelect(attrs={'id':'my-payment'}), queryset=data['payment_method'] if 'payment_method' in data else None,initial=0)
    image_option = forms.ModelChoiceField(widget=forms.RadioSelect(), queryset=data['image_option'] if 'image_option' in data else None,initial=0)
    image_option_or = forms.CharField(label='name_and_surename',max_length=400,widget=forms.Textarea(attrs={'type': 'text','rows':'5','class': 'form-control input-sm input-width', 'placeholder':'texte libre < 400 caractères','id':'reason'}),required=False)

class ProductModelForm(ModelForm):
    class Meta:
        model = Product

    category_key = ProductCategory.objects.filter(status=True)
    name = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control input-sm input-width','id':'name'}))
    category = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize select-width','id':'category'}), queryset=category_key)
    description = forms.CharField(max_length=1000,widget=forms.Textarea(attrs={'type': 'text','rows':'5','class': 'form-control input-sm input-width', 'placeholder':'texte libre < 1000 caractères','id':'description'}))
    image = forms.ImageField(label='image',max_length=200,required=True)
    price = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control input-sm input-width','id':'price'}))
    shipping_charge = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control input-sm input-width','id':'price'}))
    availability = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control input-sm input-width datepicker','id':'availabile'}))
    link = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control input-sm input-width','id':'link'}))
    sort = forms.CharField(widget=forms.TextInput(attrs={'type': 'hidden','class':'form-control input-sm input-width','value':0,'id':'sort'}),required=False)

class ProductEmailForm(forms.Form):
    email =  forms.CharField(widget=forms.TextInput(attrs={'type': 'email', 'placeholder':'Email','class':'form-control','required':'required'}))    
    product = forms.CharField(widget=forms.TextInput(attrs={'type': 'hidden','class':''}),required=False)

class ProductAbuseForm(ModelForm):
    class Meta:
        model = ProductAbuse

    user = forms.HiddenInput()
    product = forms.HiddenInput()

class MysaleForm(ModelForm):
    class Meta:
        model = Offer
    offer_key = Offer.objects.filter(status=True)
    offers = forms.ModelChoiceField(widget=forms.RadioSelect, queryset=offer_key)
    country = forms.ChoiceField(label='country',widget=forms.Select(attrs={'class':'custom-selectize','placeholder':'pays'}), choices=countries, initial='FR')

class subscriptionForm(ModelForm):
    class Meta:
        model = Subscription

    PayMethod = (
                (u"paiement mensuel par virement bancaire",u"paiement mensuel par virement bancaire"),
                ('paiement trimestriel par chèque','paiement trimestriel par chèque')
            )  
    tit = (
            (u"M.",u"M."),
            ('Mme','Mme'),
            ('Mlle','Mlle')
        )          
    offer_key_product = Offer.objects.filter(status=True,offer_type=0)
    offer_key_destock = Offer.objects.filter(status=True,offer_type=1)
    offer_product = forms.ModelChoiceField(widget=forms.RadioSelect, queryset=offer_key_product, empty_label=None, required=False) 
    offer_destock = forms.ModelChoiceField(widget=forms.RadioSelect, queryset=offer_key_destock, empty_label=None, required=False)    
    company_name = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control'}),required=True)
    manager_name = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control'}),required=True)      
    email = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control'}),required=False)
    payment_method = forms.ChoiceField(label='Language',required=True,widget=forms.RadioSelect, choices=PayMethod,initial='paiement mensuel par virement bancaire')
    title = forms.ChoiceField(label='title',required=False,widget=forms.Select(attrs={'class': 'custom-selectize'}), choices=tit,initial='Mr')
    country = forms.ChoiceField(label='country',widget=forms.Select(attrs={'class':'custom-selectize','placeholder':'pays'}), choices=countries, initial='FR')
    contact_number = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control'}),required=True)
    campany_address = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control'}),required=True)
    campany_post = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control'}),required=True)
    campany_state = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control','id':'add-classfied-location'}),required=False)
    campany_url = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control'}),required=False)
    client_fname = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control'}),required=False)
    client_email = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control'}),required=False)
    client_phone = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control'}),required=False)
    campany_city = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control'}),required=False)
    terms = forms.BooleanField(widget=forms.TextInput(attrs={'type': 'checkbox','required':'required','data-field':'terms'}),required=True)
    latitude = forms.HiddenInput()
    longitude = forms.HiddenInput()


class CreateemailalertForm(ModelForm):
    class Meta:
        model = Createemailalert

    price_keys = ClassifiedPriceRange.objects.filter()
    implant_key = CaravaneImplantation.objects.filter(status=True) 
    keys = ChoiceKey.objects
    results = keys.prefetch_related('choices')
    choice_keys = ChoiceKey.objects.all()
    arrange = {}
    data = {}    
    for result in results:
        data[result.choice_key] = result.choices.filter(choice_key_id=result.id)
    brand_key = CaravaneBrand.objects.filter(status=True)    
    caravane_type = forms.ModelChoiceField(widget=forms.Select(attrs={'id': 'caravane_type_custom_selectize'}), queryset=data['caravane_type'] if 'caravane_type' in data else None,required=True)
    brand = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'custom-selectize'}), queryset=brand_key, required=True)
    user = forms.HiddenInput()
    implantation=forms.ModelChoiceField(widget=forms.Select(attrs={'id': 'implant_custom_selectize'}), queryset=implant_key,required=True)
    price = forms.ModelChoiceField(widget=forms.Select(attrs={'id': 'class_price_selectize'}), queryset=price_keys,required=True)
    country = forms.ChoiceField(label='country',widget=forms.Select(attrs={'id':'class_country_selectize','class':'class_country_selectize','placeholder':'pays'}),choices=countries,initial={'country': ''},required=True)

class OthersiteModelForm(ModelForm):
    class Meta:   
        model = OtherSite

    pay_option = (
                (u"Campings en Espagne",u"Campings en Espagne"),
                ('Campings en France','Campings en France')
            )     
    name  = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control'}),required=True)
    description = forms.CharField(widget=forms.Textarea(attrs={'type': 'text','class': 'form-control','rows':'3'}))
    image = forms.FileField(required=False)    
    pay_country = forms.ChoiceField(widget=forms.Select(attrs={'class':'custom-selectize'}),choices=pay_option,required=True)
    links = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control'}),required=True)
    #address  = forms.CharField(widget=forms.TextInput(attrs={'type': 'text','class':'form-control','id':'other_location'}))   

class HistorySearchForm(forms.Form):
    currentYear = datetime.datetime.now().year
    year = forms.ChoiceField(choices=[(x, x) for x in range(1999,currentYear+1)],widget=forms.Select(attrs={'class': 'custom-selectize'}),required=False)