from django import forms
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from text_unidecode import unidecode

from ...bid.models import BidSession


class BidSessionForm(forms.ModelForm):

    class Meta:
        model = BidSession
        exclude = []