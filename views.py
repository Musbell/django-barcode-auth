from backends import BarcodeAuthBackend
from django.contrib import auth
#from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.middleware.csrf import get_token
from django.shortcuts import render_to_response
from django.template import RequestContext
from forms import UserCreationForm

barcode_auth = BarcodeAuthBackend()


def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    else:
        if request.REQUEST.get('barcode_data'):
            barcode_data = request.REQUEST['barcode_data']
            try:
                username, password = barcode_data.lstrip('#').split('|')
                user = barcode_auth.authenticate(
                        username=username,
                        password=password
                        )
            except ValueError:
                user = None
            if user is not None:
                if user.is_active:
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    auth.login(request, user)
                    return HttpResponseRedirect('/')
        return render_to_response('login.html', {},
            context_instance=RequestContext(request))


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')


def register(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            print("saving form")
            form.save()
            return HttpResponseRedirect('login')
    else:
        form = UserCreationForm()
    return render_to_response("register.html", {
        'form': form,
    }, context_instance=RequestContext(request))


def profile(request, userprofile):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))
    else:
        user = User.objects.get(username=userprofile)
        if request.user == user:
            prefill = model_to_dict(user)
            print(prefill)
            form = UserCreationForm(initial=prefill)
            return render_to_response("profile.html", {
                'form': form,
                'user': user,
                }, context_instance=RequestContext(request))
