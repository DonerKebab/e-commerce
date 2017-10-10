from django.template.response import TemplateResponse

from ..dashboard.views import staff_member_required
from ..product.utils import products_with_availability, products_for_homepage


def home(request):
    products, products_categories = products_for_homepage(request)

    return TemplateResponse(
        request, 'home.html',
        {'products': products, 'parent': None, 'products_categories': products_categories})


@staff_member_required
def styleguide(request):
    return TemplateResponse(request, 'styleguide.html')
