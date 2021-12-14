from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Permission, Group
from django.db import transaction, IntegrityError
from django.shortcuts import render, redirect
from django.urls import reverse

from tenants.models import Tenant
from winget.models import Package, Version, Installer


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            try:
                tenant = form.save()
            except UserAlreadyExists:
                form.add_error(
                    'email', 'A user with this email already exists.'
                )
            else:
                login(request, tenant.user)
                return redirect(reverse('admin:winget_package_changelist'))
    else:
        form = SignupForm()
    return render(request, 'tenants/signup.html', {'form': form})


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email',)

    @transaction.atomic
    def save(self, commit=True):
        assert commit, 'commit=False is not implemented.'
        user = super().save(commit=False)
        user.username = user.email
        user.is_staff = True
        try:
            user.save()
            tenant = Tenant.objects.create(user=user)
        except IntegrityError:
            raise UserAlreadyExists()
        user.groups.add(_get_or_create_tenants_group())
        return tenant


def _get_or_create_tenants_group():
    group, created = Group.objects.get_or_create(name='Tenants')
    if created:
        for model in (Package, Version, Installer):
            for action in ('view', 'add', 'change', 'delete'):
                codename = f'{action}_{model._meta.model_name}'
                permission = Permission.objects.get(codename=codename)
                group.permissions.add(permission)
    return group


class UserAlreadyExists(IntegrityError):
    pass
