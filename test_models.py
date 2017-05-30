from django.test import TestCase
from django.db import models, IntegrityError, transaction
from lacaravane.models import Document,DocumentItem,Video,VideoComment,ContactUs,ChoiceKey,ChoiceOption,Caravane,BadCaravaneError
from django.contrib.auth.models import User
import mock
from django.core.files import File
from mock import MagicMock


file_mock = mock.MagicMock(spec=File, name='FileMock')
img_mock = mock.MagicMock(spec=File, name='ImgMock')
file_mock.name = 'test.pdf'
img_mock.name = 'test.png'

class DocumentTests(TestCase):

	def create_document(self,name,description,status,slug):
		return Document.objects.create(name=name,description=description,status=status,slug=slug)	

	def test_save(self):

		w = self.create_document(name="Testname",description="description_test",status=False,slug="")
		self.assertTrue(isinstance(w, Document))
		self.assertEqual(w.__unicode__(), w.name)

	def test_document_description(self):

		w = self.create_document(name="name",description="",status=False,slug="")
		self.assertTrue(isinstance(w, Document))
		self.assertEqual(w.for_description(), w.description)

	def test_document_max_description(self):

		x="a" * 150 	
		w = self.create_document(name="name",description=x,status=False,slug="")
		self.assertTrue(isinstance(w, Document))
		self.assertEqual(w.for_description(), w.description)
		
	def test_document_status(self):

		w = self.create_document(name="name",description="description",status=False,slug="")
		self.assertTrue(isinstance(w, Document))
		self.assertEqual(False, w.status)

	def test_document_slug(self):

		w = self.create_document(name="name",description="description",status=False,slug="")
		self.assertTrue(isinstance(w, Document))
		self.assertEqual(w.for_slug(), w.slug)


class DocumentItemTests(TestCase):

	def create_document(self,name,description,status,slug):
		return Document.objects.create(name=name,description=description,status=status,slug=slug)

	def create_user(self,username,password,email):
		return User.objects.create(username=username,password=password,email=email)	

	def create_documet_item(self,title,description,pages,language,photo,pdf,slug,status,document=Document,user=User):
		d = self.create_document(name="name",description="description",status=False,slug="")
		u =self.create_user(username="prakash",password="123546",email="admin@gmail.com")
 		return DocumentItem.objects.create(title=title,description=description,pages=pages,language=language,photo=photo,pdf=pdf,status=False,document=d,user=u)

	def test_documet_item_title(self):
		w = self.create_documet_item(title='Document',description='description',pages=10,language='Allemand',photo=img_mock.name,pdf=file_mock.name,status=False,slug='document')
		self.assertTrue(isinstance(w, DocumentItem))
		self.assertEqual(w.__unicode__(), w.title)

	def test_documet_item_page(self):
		w = self.create_documet_item(title='New document',description='description',pages=20, language='Allemand', photo=img_mock.name, pdf=file_mock.name, status=False, slug='document')
		self.assertTrue(isinstance(w, DocumentItem))
		self.assertEqual(w.for_pages(), w.pages)

	def test_documet_item_language(self):
		w = self.create_documet_item(title='New document',description='description',pages=20, language='Allemand', photo=img_mock.name, pdf=file_mock.name, status=False, slug='document')
		self.assertTrue(isinstance(w, DocumentItem))
		self.assertEqual(w.for_language(), w.language)

	def test_documet_item_photo(self):
		w = self.create_documet_item(title='New document',description='description',pages=20, language='Allemand', photo='', pdf=file_mock.name, status=False, slug='document')
		self.assertTrue(isinstance(w, DocumentItem))
		self.assertEqual(w.for_photo(), w.photo)

	def test_documet_item_pdf(self):
		w = self.create_documet_item(title='New document',description='description',pages=20, language='Allemand', photo=img_mock.name, pdf='', status=False, slug='document')
		self.assertTrue(isinstance(w, DocumentItem))
		self.assertEqual(w.for_pdf(), w.pdf)

class ContactUsTests(TestCase):

	def create_contact(self,first_name,last_name,email,message,created_at = models.DateTimeField(auto_now_add=True)):
		return ContactUs.objects.create(first_name=first_name,last_name=last_name,email=email,message=message,created_at=created_at)

	def test_ContactUs_first_name(self):
		ins = self.create_contact(first_name='Test Fname',last_name='Test Lname',email='sivaprakash@gmail.com', message='testing hello world',created_at = models.DateTimeField(auto_now_add=True))
		self.assertTrue(isinstance(ins, ContactUs))
		self.assertEqual(ins.__unicode__(), 'Test Fname')

	def test_ContactUs_last_name(self):
		ins = self.create_contact(first_name='Test Fname',last_name='Test Lname',email='sivaprakash@gmail.com', message='testing hello world',created_at = models.DateTimeField(auto_now_add=True))
		self.assertTrue(isinstance(ins, ContactUs))
		self.assertEqual(ins.last_name, 'Test Lname')

	def test_ContactUs_message(self):
		ins = self.create_contact(first_name='Test Fname',last_name='Test Lname',email='sivaprakash@gmail.com', message='message',created_at = models.DateTimeField(auto_now_add=True))
		self.assertTrue(isinstance(ins, ContactUs))
		self.assertEqual(ins.message, 'message')

	def test_ContactUs_email(self):
		ins = self.create_contact(first_name='Test Fname',last_name='Test Lname',email='admin@gmail.com', message='message',created_at = models.DateTimeField(auto_now_add=True))
		self.assertTrue(isinstance(ins, ContactUs))
		self.assertEqual(ins.email, 'admin@gmail.com')		

class ChoiceOptionTest(TestCase):

	def test_choiceOption(self):
  		choice_key = ChoiceKey.objects.create(choice_key="key")
  		ins=ChoiceOption.objects.create(choice_key=choice_key,choice_options='Option1')
  		self.assertEqual(ins.choice_options, 'Option1')
  		# self.assertTrue(isinstance(ins, ContactUs))
       	#self.assertEquals(choice_in_db.count(),1)

	    # choice_key = MagicMock(spec=ChoiceKey)
	    # choice_key._state = MagicMock()
	    # ChoiceOption.objects.create(choice_key=choice_key,choice_options='Option1')
	    # choice_option = ChoiceOption.objects.all() 
	    # self.assertEquals(choice_option.count(),1)

class CaravaneTests(TestCase):

	def create_user(self,username,password,email):
		return User.objects.create(username=username,password=password,email=email)

	def caravane_type_option(self,name,option):
		choice_key = ChoiceKey.objects.create(choice_key=name)
		option_type = ChoiceOption.objects.create(choice_key=choice_key, choice_options=option)
		return option_type

	def test_save_Caravane(self):
		caravane_name='Testing'
		user =self.create_user(username="Test",password="123546",email="admin@gmail.com")
		ins= Caravane.objects.create(user=user,caravane_name=caravane_name,slug="testing",caravane_type=self.caravane_type_option(name='caravane_type',option='option1'),brand=self.caravane_type_option(name='brand',option='option1'),model='Testing_model',manufacture_year=self.caravane_type_option(name='year',option='2014'),country_registration=self.caravane_type_option(name='reg',option='IN'),number_of_seats=self.caravane_type_option(name='seat',option='1'),weight=150,total_weight=120,curb_weight=110,payload=120,weight_in_working_order=120,other_payload1=110,other_payload2=90,other_payload3=85,other_payload4=105,external_dimension=145,boom_length=750,external_length_of_box=600,external_width_of_box=10,external_height_of_caravane=145,external_height_of_folded_catavane=800,external_developed_awning=150,internal_dimension=120,internal_length_of_box=120,internal_width_of_box=140,internal_height_of_caravane=150,internal_height_of_folded_catavane=120,bed_type_size=150,before_caravane_type=self.caravane_type_option(name='before_type',option='option1'),before_caravane_size='10',middle_caravane_type=self.caravane_type_option(name='middle_type',option='option1'),middle_caravane_size='10',back_caravane_type=self.caravane_type_option(name='back_type',option='option1'),back_caravane_size='10',drinking_water_tank=self.caravane_type_option(name='drink',option='option1'),drinking_water_capacity=150,waste_water_tank=self.caravane_type_option(name='waste_type',option='option1'),waste_water_capacity=120,battery=self.caravane_type_option(name='battery',option='option1'),battery_power=150,solar_panel=self.caravane_type_option(name='solar',option='option1'),solar_power=180,chemical_toiler=self.caravane_type_option(name='chemical',option='option1'),chemical_type=self.caravane_type_option(name='chemical_type',option='option1'),refrigerator=self.caravane_type_option(name='ref',option='option1'),refrigerator_type=self.caravane_type_option(name='ref_type',option='option1'),stove=self.caravane_type_option(name='stove',option='option1'),stove_type=self.caravane_type_option(name='stove_type',option='option1'),heating=self.caravane_type_option(name='heating',option='option1'),heating_type=self.caravane_type_option(name='heating_type',option='option1'),water=self.caravane_type_option(name='water',option='option1'),water_type=self.caravane_type_option(name='water_type',option='option1'),oven=self.caravane_type_option(name='oven',option='option1'),structure_of_caravane='Testing caravane Structure',type_of_chassis=self.caravane_type_option(name='chassis',option='option1'),shocks=self.caravane_type_option(name='shocks',option='option1'),floor_thickness=100,wall_thickness=200,roof_thickness=300,insulation_type='Test insulation_type',cover='Test cover',new_purchased_value=15,current_value=15,link_our_classified='Test link_our_classified',list_of_members='Test list_of_members',forum_post='Testing forum_post',video='Testing',status=0)
		self.assertTrue(isinstance(ins, Caravane))
		self.assertEqual(ins.pk, 1)
		caravane_in_db = Caravane.objects.all() 
		self.assertEquals(caravane_in_db.count(),1)
		caravane = caravane_in_db[0]
		self.assertEquals(caravane.caravane_name,caravane_name)

	def test_save_Caravane_type(self):
		caravane_name='Testing'
		user =self.create_user(username="Test",password="123546",email="admin@gmail.com")
		ins= Caravane.objects.create(user=user,caravane_name=caravane_name,slug="testing",caravane_type=self.caravane_type_option(name='caravane_type',option='Test_type'),brand=self.caravane_type_option(name='brand',option='option1'),model='Testing_model',manufacture_year=self.caravane_type_option(name='year',option='2014'),country_registration=self.caravane_type_option(name='reg',option='IN'),number_of_seats=self.caravane_type_option(name='seat',option='1'),weight=150,total_weight=120,curb_weight=110,payload=120,weight_in_working_order=120,other_payload1=110,other_payload2=90,other_payload3=85,other_payload4=105,external_dimension=145,boom_length=750,external_length_of_box=600,external_width_of_box=10,external_height_of_caravane=145,external_height_of_folded_catavane=800,external_developed_awning=150,internal_dimension=120,internal_length_of_box=120,internal_width_of_box=140,internal_height_of_caravane=150,internal_height_of_folded_catavane=120,bed_type_size=150,before_caravane_type=self.caravane_type_option(name='before_type',option='option1'),before_caravane_size='10',middle_caravane_type=self.caravane_type_option(name='middle_type',option='option1'),middle_caravane_size='10',back_caravane_type=self.caravane_type_option(name='back_type',option='option1'),back_caravane_size='10',drinking_water_tank=self.caravane_type_option(name='drink',option='option1'),drinking_water_capacity=150,waste_water_tank=self.caravane_type_option(name='waste_type',option='option1'),waste_water_capacity=120,battery=self.caravane_type_option(name='battery',option='option1'),battery_power=150,solar_panel=self.caravane_type_option(name='solar',option='option1'),solar_power=180,chemical_toiler=self.caravane_type_option(name='chemical',option='option1'),chemical_type=self.caravane_type_option(name='chemical_type',option='option1'),refrigerator=self.caravane_type_option(name='ref',option='option1'),refrigerator_type=self.caravane_type_option(name='ref_type',option='option1'),stove=self.caravane_type_option(name='stove',option='option1'),stove_type=self.caravane_type_option(name='stove_type',option='option1'),heating=self.caravane_type_option(name='heating',option='option1'),heating_type=self.caravane_type_option(name='heating_type',option='option1'),water=self.caravane_type_option(name='water',option='option1'),water_type=self.caravane_type_option(name='water_type',option='option1'),oven=self.caravane_type_option(name='oven',option='option1'),structure_of_caravane='Testing caravane Structure',type_of_chassis=self.caravane_type_option(name='chassis',option='option1'),shocks=self.caravane_type_option(name='shocks',option='option1'),floor_thickness=100,wall_thickness=200,roof_thickness=300,insulation_type='Test insulation_type',cover='Test cover',new_purchased_value=15,current_value=15,link_our_classified='Test link_our_classified',list_of_members='Test list_of_members',forum_post='Testing forum_post',video='Testing',status=0)
		caravane_in_db = Caravane.objects.all() 
		self.assertEquals(caravane_in_db.count(),1)
		caravane = caravane_in_db[0]
		output=str(caravane.caravane_type)
		self.assertEquals(output,'Test_type')	

	
		
				