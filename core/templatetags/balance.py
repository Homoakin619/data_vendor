from django import template
from core.models import Customer 

register = template.Library()

@register.filter
def get_balance(user):
    if user.is_authenticated:
        balance = Customer.objects.get(user=user).balance
        return balance

