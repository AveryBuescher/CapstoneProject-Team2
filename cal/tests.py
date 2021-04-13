from django.test import TestCase
from .models import Event

# Create your tests here.
class EventFilterTest(TestCase):
    def __init__(self):
        super().__init__()
        print("This part of the test works")

    def __del__(self):
        print("This part works. I think.")

    def dummyTest(self):
        self.assertIs(True, True)
