from rest_framework.generics import RetrieveAPIView

from track.models import Track, get_default_track
from track.serializers.track import TrackSerializer


class TrackAPIView(RetrieveAPIView):
    serializer_class = TrackSerializer
    queryset = Track.objects
    lookup_url_kwarg = 'track_id'

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        track_id = self.kwargs[lookup_url_kwarg]
        if track_id == 0:
            return get_default_track()

        return super().get_object()
