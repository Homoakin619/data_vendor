from django.contrib import admin

from .models import Customer,Card,Merchant,Transaction,CardTransactions





@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
	list_display = ['ref_id','phone','balance']

	search_fields = ['ref_id','phone',]

admin.site.register(Card)
# admin.site.register(Cart)
admin.site.register(Merchant)

@admin.register(Transaction)
class Transaction(admin.ModelAdmin):
	list_display = ['transaction_id','date','merchant','item_qty','successful']

	search_fields = ['transaction_id']

@admin.register(CardTransactions)
class CardTransactionAdmin(admin.ModelAdmin):
	list_display = ['user','transaction_id','date','amount','successful']
	
	search_fields = ['transation_id','date']
