from rest_framework import serializers

from track.models import Track, TrackSector


class TrackSectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackSector
        fields = ('sector_order', 'length', 'curve_radius', 'curve_direction')


class TrackSerializer(serializers.ModelSerializer):
    sectors = serializers.SerializerMethodField()

    class Meta:
        model = Track
        fields = ('id', 'name', 'sectors')

    def get_sectors(self, obj):
        sectors = obj.sectors.order_by('sector_order')
        return TrackSectorSerializer(sectors, many=True).data
