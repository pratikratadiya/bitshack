from django.shortcuts import render, redirect
from django.contrib import auth
import pyrebase
import matplotlib.pyplot as plt
from matplotlib import cm as CM
from PIL import Image
import numpy as np
import requests
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.contrib import messages
import weasyprint
from weasyprint import CSS
import io,os
from keras.models import model_from_json
import keras
from mysite import settings
from keras.models import load_model
import keras.backend as K
from myapp.utils import send_html_email
# Create your views here.

config = {
    'apiKey': "AIzaSyBmyjt2BagFjMpTl23Rh_fZjQw4n12fkxQ",
    'authDomain': "pyrecoep.firebaseapp.com",
    'databaseURL': "https://pyrecoep.firebaseio.com",
    'projectId': "pyrecoep",
    'storageBucket': "pyrecoep.appspot.com",
    'messagingSenderId': "649740044984",
    'serviceAccount': "pyrecoep.json"
}

firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database()
storage = firebase.storage()

def loads_model():
    json_file = open('model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    loaded_model.load_weights("A_keras.h5")
    return loaded_model

def create_img(path):
    im = Image.open(requests.get(path, stream=True).raw).convert('RGB')
    im = np.array(im)
    im = im/255
    im[:,:,0]=(im[:,:,0]-0.485)/0.229
    im[:,:,1]=(im[:,:,1]-0.456)/0.224
    im[:,:,2]=(im[:,:,2]-0.406)/0.225
    im = np.expand_dims(im,axis  = 0)
    return im

def predict(path):
	model = loads_model()
	image = create_img(path)
	print('Model processed')
	ans = model.predict(image)
	print('Ans predicted')
	count = np.sum(ans)
	K.clear_session()
	return ans, int(count)

def signin(request):
	return render(request, 'myapp/signin.html')

def postsign(request):
	email = request.POST.get('email')
	password = request.POST.get('pass')
	try:
		user = authe.sign_in_with_email_and_password(email,password)
	except:
		message = "Invalid credentials"
		return render(request, 'myapp/signin.html', {"msg":message})
	session_id = user['localId']
	request.session['uid'] = str(session_id)
	return redirect('welcome')

def welcome(request):
	status = database.child('details').child(request.session['uid']).child('status').get().val()
	name = database.child('details').child(request.session['uid']).child('name').get().val()
	context = {}
	context['name'] = name
	if status == 1:
		context['status'] = 1
	return render(request, 'myapp/welcome.html', context)

def logout(request):
	auth.logout(request)
	return redirect('signin')

def signup(request):
	return render(request, 'myapp/signup.html')

def postsignup(request):
    name=request.POST.get('name')
    email=request.POST.get('email')
    passw=request.POST.get('pass')
    try:
        user=authe.create_user_with_email_and_password(email,passw)
    except:
        message="Unable to create account try again"
        return render(request,"myapp/signup.html",{"messg":message})
    data = {
    	"name": name,
    	"email": email,
    	"status": 0
    }
    uid = user['localId']
    database.child('details').child(uid).set(data)
    return redirect('/')

def addevent(request):
	return render(request, 'myapp/addevent.html')

def event_create(request):
	#Just added source code for post_create function/view
	import time
	millis = time.strftime('%H:%m %b %d, %Y')
	print("mili"+str(millis))
	work = request.POST.get('work')
	time = request.POST.get('time')
	date = request.POST.get('date')
	location =request.POST.get('location')
	url = request.POST.get('url')
	time_and_date = str(time)+' '+str(date)

	a = request.session['uid']
	uname = database.child('details').child(a).child('name').get().val()

	data = {
	"place":work,
	'exact_location':location,
	'time_and_date': time_and_date,
	'uploaded_on':millis,
	'image_url':url,
	'volunteer_uid':a,
	'volunteer_name':uname,
	'count': 0
	}
	
	rep = database.child('reports')
	newrep = rep.push(data)
	name = newrep['name']
	hc, num = predict(url)
	hc = hc.squeeze()
	plt.imsave('a.jpg', hc, cmap=CM.jet)
	storage.child('heatmap/'+name+'_hmap.jpg').put('a.jpg', a)
	database.child('reports').child(str(name)).child('count').set(num)
	database.child('reports').child(str(name)).child('heatmap_url').set(str(storage.child('heatmap/'+name+'_hmap.jpg').get_url(a)))
	return redirect('event_detail', id = name)

def event_detail(request, id):
	obj = database.child('reports').child(str(id)).get()
	lis = obj.val()
	lis['uid'] = str(id)
	return render(request, 'myapp/event_detail.html', lis)

def gen_pdf(request, id):
	obj = database.child('reports').child(str(id)).get()
	lis = obj.val()
	html = render_to_string('myapp/pdf_detail.html', lis)
	response = HttpResponse(content_type = 'application/pdf')
	print("Response done")
	response['Content-Disposition'] = 'filename=report_{}'.format(str(id))+'.pdf'
	pdf = weasyprint.HTML(string=html).write_pdf()
	print("Pdf done")
	rec_email = database.child('details').child(request.session['uid']).child('email').get().val()
	print("Email fetched")
	to_email = [rec_email]
	send_html_email(pdf,to_email)
	# subject = 'Report of headcount monitoring'
	# msg = EmailMessage(subject,to=to_email)
	# msg.content_subtype = "html"
	# msg.attach('report_{}'.format(str(id))+'.pdf', pdf, "application/pdf")
	# email.content_subtype = "pdf"
	# email.encoding = 'us-ascii'
	print("Rocket launch")
	# msg.send()
	print("Rocket landed")
	return redirect('welcome')

def eventdetails(request):
	print(request.session['uid'])
	res = requests.get('https://pyrecoep.firebaseio.com/reports.json?orderBy="volunteer_uid"&equalTo="'+request.session['uid']+'"')
	res = res.json()
	lis = []
	for key,val in res.items():
		val['UID'] = key
		lis.append(val)
	return render(request, 'myapp/eventdetails.html', {'list': lis})

def allreports(request):
	res = database.child('reports').get().val()
	lis = []
	for key,val in res.items():
		val['UID'] = key
		lis.append(val)
	return render(request, 'myapp/alleventdetails.html', {'list': lis})

def raw_access(request):
	if request.method == 'POST':
		imgfile = request.FILES['imgfile']
		file_obj = imgfile.read()
		media_path = settings.MEDIA_ROOT
		file_path = '/media/upload_files'
		file = os.path.join(file_path, imgfile.name)
		with open(file, 'w+') as f:
			f.write(file_obj)
		uploaded_file = os.path.join("/media","upload_files",imgfile.name)
		hc, num = predict(uploaded_file)
		hc = hc.squeeze()
		plt.imsave('myapp/static/b.jpg', hc, cmap=CM.jet)
		return render(request, 'myapp/result.html', {'num': num})		
	return render(request, 'myapp/rawreq.html')



# Heart disease demo


# def heart_detect(request):
# 	return render(request, 'myapp/heartdet.html')

# def disease_check(request):
# 	context = {}
# 	model = load_model('heartmodel.h5')
# 	age = request.POST.get('age')
# 	sex = request.POST.get('sex')
# 	bps = request.POST.get('bps')
# 	scol = request.POST.get('scol')
# 	mhr = request.POST.get('mhr')
# 	stdp = request.POST.get('stdp')
# 	mvc = request.POST.get('mvc')
# 	thal = request.POST.get('thal')
# 	x_test = np.array([[age,sex,bps,scol,mhr,stdp,mvc,thal]])
# 	num = int(model.predict(x_test)*100)
# 	context['pred'] = num
# 	K.clear_session()
# 	return render(request,'myapp/disres.html',context)
