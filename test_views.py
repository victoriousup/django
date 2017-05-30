from django.core.urlresolvers import resolve,reverse
from django.test import Client
from django.test import TestCase
# from lacaravane.views import home
# from django.shortcuts import render, redirect, get_object_or_404
# from lacaravane.app_context import siteinfo


# from social_auth.tests.client import SocialClient

# class DocumentPageTest(TestCase):

# 	def test_rul_document_get(self):
# 		client = Client()
# 	 	response = client.post(reverse('home'))
# 	 	raise Exception(response.status_code)
# 	 	self.assertEqual(response.status_code, 200)