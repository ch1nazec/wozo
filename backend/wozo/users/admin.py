from django.contrib import admin
from .models import CustomUser, Seller, PersonalData, Agent


# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'third_name',
                    'first_name', 'last_name',
                    'email', 'phone_number',
                    'is_staff', 'date_joined']
    list_filter = [
        'third_name',
        'first_name', 'last_name',
        'email', 'phone_number',
        'is_staff', 'date_joined'
    ]
    list_editable = [
        'third_name',
        'first_name', 'last_name',
        'email', 'phone_number',
        'is_staff']
    
    list_per_page = 25
    ordering = ['-id']


# @admin.register(Worker)
# class WorkerAdmin(admin.ModelAdmin):
#     list_display = [
#         'user', 'contract_number', 'is_active']
#     list_display_links = ['user']
#     list_select_related = ['user']


@admin.register(PersonalData)
class PersonalDataAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'inn', 'snils',
        'passport_series', 'passport_number',
        'passport_issued_by', 'passport_issued_date'
        ]
    list_display_links = ['user']
    list_editable = [
        'inn', 'snils',
        'passport_series', 'passport_number',
        'passport_issued_by', 'passport_issued_date'
    ]
    list_filter = [
        'inn', 'snils',
                'passport_series', 'passport_number',
                'passport_issued_by', 'passport_issued_date'
    ]
    list_select_related = ['user']
    list_per_page = 50
    ordering = ['-id']


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ['user', 'status']
    list_display_links = ['user']
    list_editable = ['status']

    search_fields = [
        'user__third_name',
        'user__first_name',
        'user__last_name',
        'user__username',
        'status',
        'user__phone_number',
        'user__email']
    list_filter = ['user__third_name',
                   'user__first_name',
                   'user__last_name',
                   'user__username',
                   'status',
                   'user__phone_number',
                   'user__email']

    list_select_related = ['user']
    list_per_page = 50
    ordering = ['user']


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ['id', 'personal_data', 'is_active']
    list_select_related = ['personal_data']
    list_per_page = 30
    list_filter = ['personal_data__inn',
                   'personal_data__snils',
                   'personal_data__passport_series',
                   'personal_data__passport_number',
                   'personal_data__passport_issued_date']
    ordering = ['personal_data']