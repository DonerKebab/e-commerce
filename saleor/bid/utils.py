from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
import random

from .models import BidSession, ProductBidHistory



FIRST_NAME_LIST = ['phuong','chien', 'tam', 'nguyen', 'duong', 'lam', 'trang', 'hoa',
'thanh', 'thao', 'thu', 'tu', 'vi', 'nhung', 'hanh', 'van', 'ngoc', 'bich', 'anh',
'huong', 'tram', 'cham', 'chi', 'yen', 'tung', 'thang', 'nam', 'nhut', 'minh',
'hung', 'chinh', 'tuan', 'trung', 'luong', 'son', 'to', 'hien', 'kieu', 'hongnga', 'camtu',
'thanh thao', 'bichhoa', 'congphuong', 'vantoan', 'thanhson', 'oanh', 'henry', 'ducdung', 
'lechi', ' mien', 'tohien', 'hoainam', 'vuanh', 'tuyen', 'sinh', 'ut']

LAST_NAME_LIST = ['nguyen', 'tran', 'anh', 'dao', 'le', 'ta', 'thu', 'huy', 'phung', 'khuc', 'thanh', 'pham', 
'phan']

NUMBER_LIST = ['37266', '98', '146', '167', '50', '581', '0704', '86', '7906', '503']


def bid_session_for_homepage():
	user = AnonymousUser()
	now = timezone.now()
	bid_session  = BidSession.objects.filter(end_bid__gte=now,
                                start_bid__lte=now).first()
	return bid_session


def create_random_name():

    first_name = FIRST_NAME_LIST[random.randint(0, len(FIRST_NAME_LIST) - 1)]
    last_name = LAST_NAME_LIST[random.randint(0, len(LAST_NAME_LIST) - 1)]

    number_end = ''
    if random.randint(0,1):
        number_end = NUMBER_LIST[random.randint(0, len(NUMBER_LIST) - 1)]

    return '{first_name}{last_name}{number_end}'.format(first_name=first_name, last_name=last_name, number_end=number_end)
