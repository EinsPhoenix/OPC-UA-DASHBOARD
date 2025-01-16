from django.contrib import admin
from .models import EnergyData

@admin.register(EnergyData)
class EnergyDataAdmin(admin.ModelAdmin):
    list_display = ('start_timestamp', 'end_timestamp', 'marketprice', 'unit')
    search_fields = ('unit',) 
    list_filter = ('unit',) 
