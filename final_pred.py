from PIL import Image
import numpy as np
import requests

def load_model():
    from keras.models import model_from_json
    json_file = open('model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    loaded_model.load_weights("B_keras.h5")
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
    model = load_model()
    image = create_img(path)
    print('Model processed')
    ans = model.predict(image)
    print('Ans predicted')
    count = np.sum(ans)
    return ans, int(count)
