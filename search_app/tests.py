from django.test import TestCase, Client
from django.urls import reverse

# Create your tests here.

class TestSearch(TestCase):

    def test_search_function(self):
        client = Client()
        query = searchResult()
        query.query = "chair"
        query.save()

        record = searchResult.objects.get(pk = query.id)
        self.assertNotEqual(record,querys)

       