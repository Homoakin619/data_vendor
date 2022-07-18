from django.contrib import messages
from django.forms import ValidationError
from django.shortcuts import redirect, render,get_object_or_404
from django.views import generic
from django.contrib.auth import login,authenticate,logout
from django.http import HttpResponseRedirect,JsonResponse
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.crypto import get_random_string


from django.core import mail


from .models import Customer,Merchant,CardTransactions, Transaction
from .forms import CustomerForm,CustomerDetailsForm, LoginForm, MerchantForm, ChangePinForm, PinPurchaseForm

import stripe
import random
import string

def get_ref_id():
	strings = string.ascii_lowercase + string.digits
	result = ''
	for i in range(8):
		result += ''.join(random.choice(strings))
	return result

def get_activation_key():
    return get_random_string(length=45)


stripe.api_key = settings.STRIPE_KEY

def get_price(network,value):
    airtel ={'1GB':400,'2GB':750}
    mtn ={'1GB':400,'2GB':750}
    glo ={'1GB':350,'2GB':750}
    etisalat ={'1GB':350,'2GB':750}
    if network.lower() == 'airtel':
        return airtel[value]
    if network.lower() == 'mtn':
        return mtn[value]
    if network.lower() == 'glo':
        return glo[value]
    if network.lower() == 'etisalat':
        return etisalat[value]



class EditProfileView(LoginRequiredMixin,generic.View):
    template_name = 'core/edit-profile.html'
    def get(self,*args,**kwargs):
        
        query = get_object_or_404(Customer,user=self.request.user)
        context = {}
        context['form'] = CustomerDetailsForm(instance=query)
        return render(self.request,self.template_name,context=context)
    def post(self,*args,**kwargs):
        query = get_object_or_404(Customer,user=self.request.user)
        form = CustomerDetailsForm(self.request.POST,instance=query)
        if form.is_valid():
            self.request.user.save()
            form.save()
            return HttpResponseRedirect(reverse('profile'))
        return self.get(*args,**kwargs)

class ProfileView(LoginRequiredMixin,generic.View):
    template_name = 'core/profile.html'
    def get(self,*args,**kwargs):
        form = ChangePinForm()
        context = {'form':form,'error':False,'profile':True}
        context['customer'] = Customer.objects.get(user=self.request.user)
        return render(self.request,self.template_name,context=context)
    
    def post(self,*args,**kwargs):
        customer = Customer.objects.get(user=self.request.user)
        form = ChangePinForm(self.request.POST)
        context = {'form':form,'error':False}
        context['customer'] = Customer.objects.get(user=self.request.user)

        if form.is_valid():
            email = form.cleaned_data['email']
            pin = form.cleaned_data['pin']
            if email == self.request.user.email:
                customer.pin = pin
                customer.save()
                return self.get(*args,**kwargs)
            else:
                context['error'] = True
                form.add_error('email',ValidationError('Kindly enter a valid email'))
                return render(self.request,self.template_name,context=context)
        else:
            context['error'] = True
            return render(self.request,self.template_name,context=context)
        


class DashboardView(LoginRequiredMixin,generic.View):
    template_name = 'core/dash.html'
    def get(self,*args,**kwargs):
        form = PinPurchaseForm()
        context ={'form':form,'error':False,'dashboard':True}
        customer = get_object_or_404(Customer,user=self.request.user)
        context['balance'] = customer.balance
        context['stripe'] = settings.STRIPE_PK
        context['items']=Merchant.objects.all()
        return render(self.request,self.template_name,context=context)

    # post-method to purchase data
    def post(self,*args,**kwargs):
        form = PinPurchaseForm(self.request.POST)
        
        user = self.request.user
        customer = get_object_or_404(Customer,user=user)
        context = {'items':Merchant.objects.all(),'form':form,'error':False}

        if self.request.POST.get('form-name') == 'pin-form':
            if form.is_valid():
                pin = form.cleaned_data['pin']
                benef = form.cleaned_data['beneficiary']
                amount = int(form.cleaned_data['amount'])
                merchant = self.request.POST.get('merchant')
                item_qty = self.request.POST.get('quantity')
            
                user_pin = customer.pin
                recharge_self = self.request.POST.get('self_recharge',False)
 
                if int(pin) == user_pin:
                    if recharge_self is not False:
                        beneficiary = customer.phone
                    else:
                        beneficiary = benef
                    if not beneficiary:
                        context['error'] = True
                        form.add_error('beneficiary',ValidationError('Kindly select a beneficiary to recharge, or tick checkbox to recharge for self!'))
                        # messages.warning(self.request,'Kindly select a beneficiary to recharge, or tick checkbox to recharge for self!') 
                        return render(self.request,self.template_name,context)
                    else:
                        balance = customer.balance - amount
                        customer.balance = balance
                        customer.save()
                        transaction_id = get_ref_id()
                        price = get_price(merchant,item_qty)
                        transaction =Transaction.objects.create(
                                transaction_id=transaction_id, user=user, merchant=merchant, beneficiary=beneficiary, item_qty=item_qty, 
                                successful=True,price=price
                            )
                        transaction.save()
                        return HttpResponseRedirect(reverse('success'))
                else:
                    context['error'] = True
                    form.add_error('pin',ValidationError('Pin is incorrect'))
                    return render(self.request,self.template_name,context)
            else:
                context['error'] = True
                return render(self.request,self.template_name,context)
        
        else:
            amount = int(self.request.POST.get('amount'))
            token = self.request.POST.get('stripeToken')
            try:
                charge = stripe.Charge.create(
                    amount=amount*100,
                    currency='usd',
                    description='Example charged card',
                    source=token,
                    )

            except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
                print('Status is: %s' % e.http_status)
                print('Code is: %s' % e.code)
                # param is '' in this case
                print('Param is: %s' % e.param)
                print('Message is: %s' % e.user_message)
                raise ValidationError(e)
            except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
                raise ValidationError(e)
            except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
                raise ValidationError("there is an error at %s" %e.param)
            except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
                print("Message is: Authentication with Stripe's API failed")
            except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
                print(e)
                raise ValidationError(e)
            except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            #     messages.error(self.request,'Your PIN is incorrect!')
                raise ValidationError(e)
            except Exception as e:
            # Something else happened, completely unrelated to Stripe
                raise ValidationError(e)

            user = get_object_or_404(User,username=self.request.user.username)
            transaction = CardTransactions.objects.create(transaction_id=charge.id,user=user,successful=True,amount=amount)
            transaction.save()
            balance = customer.balance
            customer.balance = balance + amount
            customer.save()
            return HttpResponseRedirect(reverse('success'))



class FundWalletView(generic.View):
    template_name = 'core/payment.html'
    def get(self,*args,**kwargs):
        form = PinPurchaseForm()
        context = {'stripe': settings.STRIPE_PK,'form':form}
        return render(self.request,self.template_name,context=context)

    def post(self,request,*args,**kwargs):
        form = PinPurchaseForm(self.request.POST)
        user = self.request.user
        customer = get_object_or_404(Customer,user=user)
        context = {'stripe': settings.STRIPE_PK,'form':form}
        if form.is_valid():
            amount = int(form.cleaned_data['amount'])
            pin = int(form.cleaned_data['pin'])
            token = self.request.POST.get('stripeToken')
            user = self.request.user
            customer = get_object_or_404(Customer,user=user)
            if pin == customer.pin:
                try:
                    charge = stripe.Charge.create(
                        amount=amount*100,
                        currency='usd',
                        description='Example charged card',
                        source=token,
                        )

                except stripe.error.CardError as e:
                # Since it's a decline, stripe.error.CardError will be caught
                    print('Status is: %s' % e.http_status)
                    print('Code is: %s' % e.code)
                    # param is '' in this case
                    print('Param is: %s' % e.param)
                    messages.warning(self.request,'%s' % e.user_message)
                    return self.get(*args,**kwargs)
                    # raise ValidationError(e)
                except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                    raise ValidationError(e)
                except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                    raise ValidationError("there is an error at %s" %e.param)
                except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                    print("Message is: Authentication with Stripe's API failed")
                except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                    print(e)
                    raise ValidationError(e)
                except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                #     messages.error(self.request,'Your PIN is incorrect!')
                    raise ValidationError(e)
                except Exception as e:
                # Something else happened, completely unrelated to Stripe
                    raise ValidationError(e)

                user = get_object_or_404(User,username=self.request.user.username)
                transaction = CardTransactions.objects.create(transaction_id=charge.id,user=user,successful=True,amount=amount)
                transaction.save()
                balance = customer.balance
                customer.balance = balance + amount
                customer.save()
                return HttpResponseRedirect(reverse('success'))
            else:
                form.add_error('pin',ValidationError('Incorrect PIN! Retry'))
                return render(self.request,self.template_name,context)
        else:
            return render(self.request,self.template_name,context)



def success(request):
    return render(request,'core/success.html',{'message':'Transaction successful You will be credited soon!'})


def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')


class TransactionHistoryView(LoginRequiredMixin,generic.View):
    template_name = 'core/transaction.html'
    def get(self,*args,**kwargs):
        transactions = Transaction.objects.filter(user=self.request.user).order_by('-id')
        context = {'transactions':enumerate(transactions,start=1),'transaction':True}
        return render(self.request,self.template_name,context=context)



class AdminHomepage(LoginRequiredMixin,generic.View):
    template_name = 'core/admins/homepage.html'
    def get(self,*args,**kwargs):

        return render(self.request,self.template_name)

class AdminTransactions(LoginRequiredMixin,generic.View):
    template_name = 'core/admins/transactions.html'
    def get(self,*args,**kwargs):
        context = {'transactions':enumerate(Transaction.objects.all().order_by('-id'),start=1),'transaction':True}
        return render(self.request,self.template_name,context=context)

class AdminListUsers(LoginRequiredMixin,generic.ListView):
    template_name = 'core/admins/users.html'
    model = User
    context_object_name = 'customers'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = True
        return context

class AdminListMerchants(LoginRequiredMixin,generic.ListView):
    model = Merchant
    template_name = 'core/admins/merchants.html'
    context_object_name = 'merchants'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['merchant'] = True
        return context
    

class AdminEditMerchant(LoginRequiredMixin,generic.View):
    template_name = 'core/admins/edit_merchant.html'

    def get(self,*args, **kwargs):
        query = get_object_or_404(Merchant,id=self.kwargs['id'])
        form = MerchantForm(instance=query)
        context = {'form':form }
        return render(self.request,self.template_name,context=context)

    def post(self,*args,**kwargs):
        query = get_object_or_404(Merchant,id=self.kwargs['id'])
        form = MerchantForm(self.request.POST,instance=query)
        context = {'form':form }
        if form.is_valid:
            form.save()
            return HttpResponseRedirect(reverse('merchants'))
        return render(self.request,self.template_name,context=context)


class IndexView(generic.View):
    template_name = 'core/login.html'
    def get(self,*args,**kwargs):
        if self.request.user.is_authenticated:
            if self.request.user.is_staff:
                return HttpResponseRedirect(reverse('admins'))
            else:
                return HttpResponseRedirect('dashboard')
        form = CustomerForm()
        login_form = LoginForm()
        context = {'form':form,'login_form':login_form,'disp':False}

        return render(self.request,self.template_name,context=context)
    
    def post(self,*args,**kwargs):
        form = CustomerForm(self.request.POST or None)
        login_form = LoginForm(self.request.POST or None)
        context = {'form':form,'login_form':login_form,'disp':False}

        login_f = self.request.POST.get('login')
        signup = self.request.POST.get('signup')

        if login_f:
            if login_form.is_valid():
                username = login_form.cleaned_data['username']
                password = login_form.cleaned_data['password']
                user = authenticate(self.request,username=username,password=password)
                if user is not None:
                    login(self.request,user)
                    if self.request.user.is_staff:
                        return HttpResponseRedirect(reverse('admins'))
                    else:
                        return HttpResponseRedirect(reverse('dashboard'))
                else:
                    context['errors'] = login_form.errors
                    return render(self.request,self.template_name,context=context)
            else: 
                context['errors'] = login_form.errors
                return render(self.request,self.template_name,context=context)

        elif signup is not None:
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password1']
                email = form.cleaned_data['email']
                activation_key = get_activation_key()
                form.save()
                user = User.objects.get(username=username)
                customer = Customer.objects.get(user=user)
                customer.activation_key = activation_key
                customer.save()
                subject = 'Zeedah Account Verification'
                body = f'Hi {username} \n Please click on the link below to confirm your registration \n http://zeedah.herokuapp.com/activate/{activation_key}'
                sender = 'zeedah@gmail.com'
                with mail.get_connection() as connection:
                    mail.EmailMessage(
                        subject, body, sender, [email],
                        connection=connection,
                    ).send()
                messages.success(self.request,'Kindly Check Your Email for link to activate your account')

                return self.get(*args,**kwargs)
            else:
                context = {'form':form,'disp':True,'errors':form.errors}
                return render(self.request,self.template_name,context=context)
        return render(self.request,self.template_name,context=context)

def activate(request,activation_key):
    customer = get_object_or_404(Customer,activation_key=activation_key)
    if customer.user.is_active == True:
        return HttpResponseRedirect(reverse('login_page'))
    else:    
        if request.method == 'POST':
            user = customer.user
            user.is_active = True
            user.save()
            customer.verified = True
            customer.save()
            return HttpResponseRedirect(reverse('login_page'))
    return render(request,'core/activation.html')