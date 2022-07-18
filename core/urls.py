from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,re_path

from . import views

urlpatterns = [
		path('dashboard/',views.DashboardView.as_view(),name='dashboard'),
		path('logout/',views.logout_user,name='logout'),
		path('profile/',views.ProfileView.as_view(),name='profile'),
		path('profile/edit/',views.EditProfileView.as_view(),name='edit-profile'),
		path('profile/transactions/',views.TransactionHistoryView.as_view(),name='transactions'),
		path('wallet/fund/',views.FundWalletView.as_view(),name='fund'),


		
		path('admins/backend/',views.AdminHomepage.as_view(),name='admins'),
		path('admins/backend/transactions/',views.AdminTransactions.as_view(),name='transaction'),
		path('admins/backend/customers/',views.AdminListUsers.as_view(),name='users'),
		path('admins/backend/merchants/',views.AdminListMerchants.as_view(),name='merchants'),
		path('admins/backend/edit_merchant/<int:id>/',views.AdminEditMerchant.as_view(),name='edit_merchant'),
		# path('admins/backend/edit_customer/<int:id>/',views.AdminEditCustomer.as_view(),name='edit_customer'),

		re_path(r'^activate/(?P<activation_key>.+)$', views.activate,name='activate'),
		path('success/',views.success,name='success'),
		path('',views.IndexView.as_view(),name='login_page')
		
]

urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)