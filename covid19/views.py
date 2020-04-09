from django.shortcuts import render
from django.conf import settings


def corona_heatmap(request):
    """
    renders the heatmap to search quarantined nearby.
    """
    return render(request, "corona_heatmap.html", {'API_KEY': settings.GOOGLE_API_KEY})
