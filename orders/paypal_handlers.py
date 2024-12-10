from paypal.standard.ipn.forms import PayPalIPNForm
from django.http import HttpResponse
from orders.models import Order

def paypal_ipn(request):
    ipn_obj = PayPalIPNForm(request.POST)

    if ipn_obj.is_valid():
        # Проверяем, что это успешный платеж
        if ipn_obj.cleaned_data['payment_status'] == "Completed":
            # Получаем ID заказа из поля invoice (или другого поля, которое вы используете)
            order_id = ipn_obj.cleaned_data['invoice']

            try:
                # Ищем заказ
                order = Order.objects.get(pk=order_id)
                # Обновляем статус заказа
                order.is_paid = True
                order.status = "Оплачен"
                order.save()
                return HttpResponse(status=200)
            except Order.DoesNotExist:
                return HttpResponse("Order not found", status=404)
        else:
            # Если платеж не успешен
            return HttpResponse("Payment not completed", status=400)
    else:
        return HttpResponse("Invalid IPN", status=400)
