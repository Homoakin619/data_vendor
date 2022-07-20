from django.shortcuts import redirect,get_object_or_404
from django.core.exceptions import ImproperlyConfigured

from core.models import Customer

class NotVerifiedMixin:
    """
    A mixin to redirect non verified users to a custom page 
    requesting them to verify their accounts before gaining 
    access to the full functionalities of the web app.

    Redirect user to redirect_url if test_func() returns False
    """

    redirect_url = None

    def get_redirect_url(self):
        redirect_url = self.redirect_url
        if not redirect_url:
            raise ImproperlyConfigured(
                '{0} is missing redirect_url attribute. Define {0}.redirect_url to overide get_redirect_url() method'.format(self.__class__.__name__)
            )

class CheckVerificationMixin(NotVerifiedMixin):
    def test_func(self):
        user = self.request.user 
        customer = get_object_or_404(Customer,user=user)
        if not customer.verified:
            return True