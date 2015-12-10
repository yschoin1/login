from django.contrib import admin
from .models import nomatUser
from .forms import nomatUserForm

# Login admin page display settings
class nomatUserAdmin(admin.ModelAdmin):
	list_display = ['__unicode__', 'confirmationCode', 'agreeToConditions']
	form = nomatUserForm

# Registered the change
admin.site.register(nomatUser, nomatUserAdmin)