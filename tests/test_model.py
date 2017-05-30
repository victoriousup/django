from django.test import TestCase
from lacaravane.models import ChoiceKey,ChoiceOption,Caravane

class ChoicesTestCase(TestCase):
	def setUp(self):
		choice_key = ChoiceKeys.create(choice_key='test', hello='123')
		choice_opt = ChoiceOption(event=ChoiceKey.create(choice_options='test2', hello='test'))
		choice_opt.full_clean()
		choice_opt.save()
		self.assertEqual(ChoiceOption.objects.filter(event__choice_options='test2').count(), 0)