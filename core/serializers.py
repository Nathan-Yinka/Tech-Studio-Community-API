from rest_framework import serializers

class CSVFileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
