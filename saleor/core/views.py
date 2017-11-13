from django.template.response import TemplateResponse

from ..dashboard.views import staff_member_required
from ..product.utils import products_with_availability, products_for_homepage
from ..bid.utils import bid_session_for_homepage

def home(request):
    products = products_for_homepage()[:12]
    bid_session = bid_session_for_homepage()
    products = products_with_availability(
        products, discounts=request.discounts, local_currency=request.currency)
    return TemplateResponse(
        request, 'home.html',
        {'products': products, 'parent': None, 'bid_session': bid_session})


@staff_member_required
def styleguide(request):
    return TemplateResponse(request, 'styleguide.html')
