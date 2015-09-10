from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm

def index(request):
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by no. likes in descending order.
    # Retrieve the top 5 only - or all if less than 5.
    # Place the list in our context_dict dictionary which will be passed to the template engine.
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}

    visits = request.session.get('visits')
    if not visits:
	visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        # Cast the value to a Python date/time object.
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        # If it's been more than a day since the last visit...
        if (datetime.now() - last_visit_time).seconds > 0:
            visits = visits + 1
            # ...and flag that the cookie last visit needs to be updated
            reset_last_visit_time = True
    else:
        # Cookie last_visit doesn't exist, so flag that it should be set.
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] =  visits
    context_dict['visits'] = visits
    
    response = render(request, 'rango/index.html', context_dict)
    # Return response back to the user, updating any cookies that need changed.
    return response


def about(request):
	if request.session.get('visits'):
		count = request.session.get('visits')
	else:
		count = 0

	return render(request, 'rango/about.html', {'visits': count}) #"Rango says here is the about page")# <a href='rango/'>Index</a>))

def category(request, category_name_slug):
	# Create context dictionary 
	context_dict = {}

	try:
	# Can we find a category name slug with the given name?
	# If we can't the .get() method raises a DoesNotExist exception.
	# So the .get() method returns one models instance or raises an exception.
		category = Category.objects.get(slug=category_name_slug)
		context_dict['category_name'] = category.name
	
	# Retrieve all of the associated pages.
	# Note that filter returns >= 1 model instance.
		pages = Page.objects.filter(category=category)

	#Adds our results list to the template context under name pages.
		context_dict['pages'] = pages
	# We also add the category object from the database to the context dictionary
	# Used in template to veryfy that the category exists.
		context_dict['category'] = category
		context_dict['category_name_slug'] = category.slug

        except Category.DoesNotExist:
	#Don't do aything - the template displays "no category" for us
		return render(request, 'rango/categorynull.html', context_dict)

	#Render the response and return it to the client
	return render(request, 'rango/category.html', context_dict)

@login_required
def add_category(request):
	# A HTTP POST?
	if request.method == 'POST':
		form = CategoryForm(request.POST)
	
	# Have we been provided with a valid form?
		if form.is_valid():
	# Save the new category to the database.
			form.save(commit=True)

	# Now call the index() view.
	# The user will be shown the homepage.
			return index(request)
		else:
		# The supplied form contained errors - so print them to terminal
			print form.errors
	else:
		#If the category was not a POST, display the form to enter details.
		form = CategoryForm()

	# Bad form (or form details), no form supplied...
	# Render the form with error messages (if any).
	return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):

	try:
		cat = Category.objects.get(slug=category_name_slug)
	except Category.DoesNotExist:
		cat = NULL

	if request.method == 'POST':
		form = PageForm(request.POST)
		if form.is_valid():
			if cat:
				page = form.save(commit=False)
				page.category = cat
				page.views = 0
				page.save()
				#Probably better to use a redirect here.
				return category(request, category_name_slug)
		else:
			print form.errors
	else:
		form = PageForm()

	context_dict = {'form':form, 'category': cat}
	
	return render(request, 'rango/add_page.html', context_dict)

def register(request):
	#Boolean to tell if the template registration was sucessfull, False = Not register (Kinda obvious)
	registered = False

	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		if user_form.is_valid() and profile_form.is_valid():
			# Save the user's form data to the database.
			user = user_form.save()
			# Now we hash the password the set_password method.
			# Once hashed, we can update the user object.
			user.set_password(user.password)
			user.save()
			
			# Sort out the UserProfile instance
			# Since we need to set the user attribute ourselves, we set commit=false
			# This delays saving the model until we're ready to avoid integrity problems.
			profile = profile_form.save(commit=False)
			profile.user = user

			# Did the user provide a profile picture?
			# If so, we need to get it from the input form and put it in the UserProfile model.
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']
			#Save the UserProfile model instance.
			profile.save()
			#Update our variable to tell the template registration was sucessfull
			registered = True

		# Invalid form or forms - mistakes or something else?
		# Print problems to the terminal.
		# They' ll also be shown to the user
		else:
			print user_form.errors, profile_form.errors
	# Not a HTTP POST< so we render our form using two ModelForm instances.
	# These forms will be balnk, ready for user input.
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()
	
	# Render the template depending on the context.
	return render(request,
		'rango/register.html',
		{'user_form': user_form, 'profile_form': profile_form, 'registered': registered} )
	

def user_login(request):

	# If the request is a HTT POST, try to pull out the relevant info.
	if request.method == 'POST':
	# Gather the username and password provided by the user
	# This information is obtained from the login form.
		# We use request.POST.get('<variable>') as opposed to request.POST['<variable>']
		#because the request.POST>get('<Variable>) returns None, if the value does not exist,
		# while the request.POST[<variable>'] will raise key error exception
		username = request.POST.get('username')
		password = request.POST.get('password')
		# Use Django's machinery to attempt to see if the username/password
		# combination is valid - a User object is returned if it is
		user = authenticate(username=username, password=password)
			
		# If we have a User object, details are correct
		# If none, no user with mathching credentials was found
		if user:
			#Was account disabled?
			if user.is_active:
			# If the account is valid and active, we can log the user in.
			# We'll shen the user back to the homepage.
				login(request, user)
				return HttpResponseRedirect('/rango')
			else:
				# An inactive account was used = no loggin in!
				return HttpResponse("Your dolarexchange account was banned for child pornography")
		else:
			# Bad login details were provided
			print "Invalid login details: {0}, {1}".format(username, password)
			return HttpResponse("Invalid login details supplied.")
		# The request is not a HTTP POST, so display the login form.
		# Most likely HTTP GET
	else:
		# No context variable to pass to the template system, hence the dictionary
		return render(request, 'rango/login.html', {})

@login_required
def restricted(request):
	return HttpResponse("Since you're logged in, you can see this text!")

@login_required
def user_logout(request):
	logout(request)
	# Back to homepagee
	return HttpResponseRedirect('/rango/')
