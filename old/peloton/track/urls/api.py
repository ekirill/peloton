from django.urls import path

from track.views import TrackAPIView

app_name = 'track'
urlpatterns = [
    path('<int:track_id>/', TrackAPIView.as_view(), name='track')
]
