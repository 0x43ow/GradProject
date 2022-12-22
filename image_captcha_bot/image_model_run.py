import torch

animals = {
    '0' : 'elephant',
    '1' : 'bear',
    '2' : 'tiger',
    '3' : 'tapir',
    '4' : 'boar'
}

def predict(image):
    prediction = model(image)
    prediction_s = str(prediction)
    if "no detections" in prediction_s:
        return None
    prediction_string = str(prediction).splitlines()[0].split(' ')[4][0]
    return(animals[prediction_string])


model = torch.hub.load('ultralytics/yolov5','custom', path='animals_classification_model.pt',force_reload=True,verbose=False,skip_validation=True)
