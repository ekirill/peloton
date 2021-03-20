from django.test import TestCase

from track.models import Track


class BasicTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.track = Track.objects.create(name='test_track')
