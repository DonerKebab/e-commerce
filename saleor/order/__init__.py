from django.utils.translation import pgettext_lazy


class OrderStatus:
    NEW = 'pending'
    CANCELLED = 'cancelled'
    SHIPPED = 'shipped'
    READY_TO_SHIP= 'ready_to_ship'
    RETURNED = 'returned'
    SHIPPED='shipped'
    FAILED = 'failed'
    DELIVERED = 'delivered'


    CHOICES = [
        (NEW, pgettext_lazy('order status', 'Chờ xác nhận')),
        (READY_TO_SHIP, pgettext_lazy('order status', 'Sẵn sàng giao hàng')),
        (CANCELLED, pgettext_lazy('order status', 'Bị huỷ')),
        (SHIPPED, pgettext_lazy('order status', 'Đã giao hàng')),
        (RETURNED, pgettext_lazy('order status', 'Bị trả lại')),
        (DELIVERED, pgettext_lazy('order status', 'Đã chuyển hàng')),
        ]
