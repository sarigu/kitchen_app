from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from .custom_renderers import JPEGRenderer, PGNRenderer
from rest_framework.response import Response
from images.models import Images


# Create your views here.

class get_image(generics.RetrieveAPIView):
    renderer_classes = [PGNRenderer]
    #send image object
    def get(self, request, *args, **kwargs):
        image = Images.objects.get(id=self.kwargs['id']).image
        return Response(image, content_type='image/png')


class images(generics.RetrieveAPIView):
    def get(self, request,):
        #get list with all image ids
        imageIDs = Images.objects.values_list('pk', flat=True)
        return Response(imageIDs)
