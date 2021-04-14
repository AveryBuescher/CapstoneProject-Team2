from django.test import TestCase
from .models import Event

from .views import filter_events_by_date
from datetime import datetime, time, date
from django.contrib.auth.models import User



# Create your tests here.
# Tests for filtering events by date
class EventFilterTest(TestCase):
    def setUp(self):
        dummya = User(password='password', username='dummya')
        dummya.save()
        self.a_id = dummya.id
        dummyb = User(password='password', username='dummyb')
        dummyb.save()
        self.b_id = dummyb.id


    def quick_event_create(self, start_datetime, end_datetime, user_id):
        foo = Event(title="Test Event", description="Test Event",
                    start_time = start_datetime,
                    end_time=end_datetime, the_user_id=user_id)
        foo.save()
        return foo

    def quick_assert_in_range(self, event, expected_value=True,
                              user_id=1):
        self.assertIs(event in filter_events_by_date(
            date(2021, 1, 4), date(2021, 1, 6), user_id),
                      expected_value)

    def test_single_date_out_of_range(self):
        foo = self.quick_event_create(datetime(2021, 1, 3),
                                      datetime(2021, 1, 3), self.a_id)
        self.quick_assert_in_range(foo, False)

    def test_single_date_in_range(self):
        foo = self.quick_event_create(date(2021, 1, 5), date(2021, 1,
                                                        5), self.a_id)
        self.quick_assert_in_range(foo)

    def test_multiple_dates_partially_in_range(self):
        foo = self.quick_event_create(date(2021, 1, 6), date(2021, 1,
                                                        7), self.a_id)
        self.quick_assert_in_range(foo, False)

    def test_wrong_user(self):
        foo = self.quick_event_create(date(2021, 1, 5), date(2021, 1,
                                                        5), self.b_id)
        self.quick_assert_in_range(foo, False, self.b_id)

