from rest_framework import serializers


class HealthStatusSerializer(serializers.Serializer):
    name = serializers.CharField(source='identifier')
    status = serializers.CharField(max_length=20, source='pretty_status')
    time_taken = serializers.FloatField()


class HealthSerializer(serializers.Serializer):
    data = HealthStatusSerializer(source='*', many=True)
