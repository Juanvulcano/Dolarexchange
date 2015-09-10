from django.shortcuts import render
#def base(request):
        #about_Dict = {'boldmessage': "Wow it's really working"}
        #return render_to_response('base.html', RequestContext(request)) #"Rango says here is the about page")# <a href='rango/'>Index</a>))

def base(request):
	if request.session.test_cookie_worked():
		 print ">>>> TEST COOKIE WORKED!"
                 request.session.delete_test_cookie()

        about_Dict = {'boldmessage': "Wow it's really working"}
        return render(request, 'base.html', about_Dict)
