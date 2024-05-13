from django.shortcuts import redirect
# decorator to redirect authenticated users to the index view.

def redirect_authenticated_user(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('store:index')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper