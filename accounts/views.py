from django.shortcuts import render

# Create your views here.

def account(request, username):
    context = {
        'a': 'b',
    }
    return render(request, 'accounts/account.html', context)
