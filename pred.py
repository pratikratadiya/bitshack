from keras.models import load_model
from numpy import array

a = load_model('heartmodel.h5')

#print(a.summary())
b = array([[14,1,3,4,7,8,2,3]])
print(a.predict_proba(b))
print(a.predict_classes(b))
print(int(a.predict(b)[0][0]*100))
