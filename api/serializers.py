from rest_framework import serializers
from images.models import Images

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'title')
        model = Images