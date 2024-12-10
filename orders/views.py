from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid

from carts.models import Cart
from orders.forms import CreateOrderForm
from orders.models import Order, OrderItem

@login_required
def create_order(request):
    if request.method == 'POST':
        form = CreateOrderForm(data=request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = request.user
                    cart_items = Cart.objects.filter(user=user)

                    if cart_items.exists():
                        order = Order.objects.create(
                            user=user,
                            phone_number=form.cleaned_data['phone_number'],
                            requires_delivery=form.cleaned_data['requires_delivery'],
                            delivery_address=form.cleaned_data['delivery_address'],
                            payment_on_get=form.cleaned_data['payment_on_get'],
                        )
                        for cart_item in cart_items:
                            product = cart_item.product
                            name = product.name
                            price = product.sell_price()
                            quantity = cart_item.quantity

                            if product.quantity < quantity:
                                raise ValidationError(
                                    f'Недостаточное количество товара {name} на складе. В наличии - {product.quantity}'
                                )

                            OrderItem.objects.create(
                                order=order,
                                product=product,
                                name=name,
                                price=price,
                                quantity=quantity,
                            )
                            product.quantity -= quantity
                            product.save()

                        cart_items.delete()

                        if form.cleaned_data['payment_on_get'] == "0":  # PayPal
                            paypal_dict = {
                                "business": settings.PAYPAL_RECEIVER_EMAIL,
                                "amount": str(order.total_cost()),
                                "item_name": f"Order {order.id}",
                                "invoice": str(uuid.uuid4()),
                                "currency_code": "USD",
                                "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
                                "return_url": request.build_absolute_uri(reverse('orders:paypal_success', args=[order.id])),
                                "cancel_return": request.build_absolute_uri(reverse('orders:paypal_cancel')),
                            }
                            paypal_form = PayPalPaymentsForm(initial=paypal_dict)
                            context = {
                                "order": order,
                                "paypal_form": paypal_form,
                            }
                            return render(request, "orders/paypal_payment.html", context)

                        messages.success(request, 'Заказ оформлен!')
                        return redirect('user:profile')
            except ValidationError as e:
                form.add_error(None, str(e))
    else:
        initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        }
        form = CreateOrderForm(initial=initial)

    context = {
        'title': 'Главная - Оформление заказа',
        'form': form,
        'orders': True,
    }
    return render(request, 'orders/create_order.html', context)


def paypal_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.is_paid = True
    order.save()
    messages.success(request, "Платеж успешно завершен!")
    return redirect('user:profile')


def paypal_cancel(request):
    messages.error(request, "Вы отменили платеж.")
    return redirect('orders:create_order')