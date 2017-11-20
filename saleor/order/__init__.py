from django.utils.translation import pgettext_lazy


class OrderStatus:
    NEW = 'pending'
    CANCELLED = 'cancelled'
    SHIPPED = 'shipped'
    PAYMENT_PENDING = 'payment-pending'
    FULLY_PAID = 'fully-paid'
    READY_TO_SHIP= 'ready_to_ship'
    RETURNED = 'returned'
    SHIPPED='shipped'
    FAILED = 'failed'
    DELIVERED = 'delivered'


    CHOICES = [
        (NEW, pgettext_lazy('order status', 'Processing')),
        (READY_TO_SHIP, pgettext_lazy('order status', 'Ready to ship')),
        (CANCELLED, pgettext_lazy('order status', 'Cancelled')),
        (SHIPPED, pgettext_lazy('order status', 'Shipped')),
        (PAYMENT_PENDING, pgettext_lazy('order status', 'Payment pending')),
        (FULLY_PAID, pgettext_lazy('order status', 'Fully paid')),
        (RETURNED, pgettext_lazy('order status', 'Returned')),
        (DELIVERED, pgettext_lazy('order status', 'Delivered')),
        ]
