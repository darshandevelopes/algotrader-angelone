from django.contrib import admin
from .models import Trade

class TradeAdmin(admin.ModelAdmin):
    list_display = ('id', 'stock1', 'stock2', 'quantity', 'entry', 'entry_diff', 'exit', 'exit_diff', 'stop_loss', 'stop_loss_diff', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('stock1', 'stock2')
    ordering = ('-created_at',)

admin.site.register(Trade, TradeAdmin)
