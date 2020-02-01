from PIL import Image
import numpy as np

def load_model():
    from keras.models import model_from_json
    json_file = open('model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    loaded_model.load_weights("model_file.h5")
    return loaded_model

def create_img(path):
    im = Image.open(path).convert('RGB')
    im = np.array(im)
    im = im/255
    # Any other preprocessing
    return im

def predict(path):
    model = load_model()
    image = create_img(path)
    ans = model.predict(image)
    return ans
