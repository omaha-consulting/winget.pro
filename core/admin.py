from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

class AdminSiteWithCustomModelOrder(AdminSite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order = {}
    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        for app in app_list:
            app['models'].sort(key=lambda m:
                self.order.get(app['app_label'] + '.' + m['object_name'], 0)
            )
        return app_list
    def register_with_order(self, model, admin_class, order):
        self.order[model._meta.label] = order
        self.register(model, admin_class)

site = AdminSiteWithCustomModelOrder()
site.register(User, UserAdmin)