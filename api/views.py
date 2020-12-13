from django.shortcuts import render
from rest_framework import generics
from .custom_renderers import JPEGRenderer, PGNRenderer
from rest_framework.response import Response
from images.models import Images

# Create your views here.
class getImage(generics.RetrieveAPIView):
    renderer_classes = [JPEGRenderer]
    renderer_classes = [PGNRenderer]

    def get(self, request, *args, **kwargs):
        queryset = Images.objects.get(id=self.kwargs['id']).image
        data = queryset
        return Response(data, content_type='image/jpg')