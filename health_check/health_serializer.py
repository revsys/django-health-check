from rest_framework import serializers


class HealthStatusSerializer(serializers.Serializer):
    name = serializers.CharField(source='identifier', default=None)
    status = serializers.CharField(source='pretty_status', default=None)
    time_taken = serializers.FloatField(default=None)


class HealthSerializer(serializers.Serializer):
    data = HealthStatusSerializer(source='*', many=True)
