from django.contrib import admin
from .models import ConfidentialData, NonConfidentialData, ChatMemory

admin.site.register(ConfidentialData)
admin.site.register(NonConfidentialData)
admin.site.register(ChatMemory)
