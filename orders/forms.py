import re
from django import forms


class CreateOrderForm(forms.Form):
    first_name = forms.CharField(
        label="Имя",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Введите ваше имя"}),
    )
    last_name = forms.CharField(
        label="Фамилия",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Введите вашу фамилию"}),
    )
    phone_number = forms.CharField(
        label="Номер телефона",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Например: 1234567890"}),
    )
    requires_delivery = forms.ChoiceField(
        label="Нужна ли доставка?",
        choices=[
            ("1", "Да, нужна доставка"),
            ("0", "Нет, самовывоз"),
        ],
        widget=forms.RadioSelect,
    )
    delivery_address = forms.CharField(
        label="Адрес доставки",
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 2, "placeholder": "Введите адрес доставки"}
        ),
        required=False,
    )
    payment_on_get = forms.ChoiceField(
        label="Способ оплаты",
        choices=[
            ("0", "Оплата картой"),
            ("1", "Оплата при получении"),
        ],
        widget=forms.RadioSelect,
    )

    def clean_phone_number(self):
        data = self.cleaned_data["phone_number"]

        # Проверка на цифры и длину 10 символов
        pattern = re.compile(r"^\d{10}$")
        if not pattern.match(data):
            raise forms.ValidationError("Номер телефона должен содержать 10 цифр без пробелов.")

        return data

    def clean(self):
        cleaned_data = super().clean()

        requires_delivery = cleaned_data.get("requires_delivery")
        delivery_address = cleaned_data.get("delivery_address")

        if requires_delivery == "1" and not delivery_address:
            self.add_error("delivery_address", "Необходимо указать адрес доставки, если доставка выбрана.")

        return cleaned_data
