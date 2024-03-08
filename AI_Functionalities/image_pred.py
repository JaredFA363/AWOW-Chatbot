from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

def predict_image(filename):
    model = load_model("tuned_wow_model.h5") #or untuned_wow_model.h5 for the lower accuracy
    # Load and preprocess the image
    img = image.load_img(filename, target_size=(200, 200))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0

    # Make predictions with the model
    predictions = model.predict(img_array)
    predicted_class_index = np.argmax(predictions)
    predicted_classes = ["Burj Khalifa", "Christ the Redeemer", "Pyramids of Giza", "Roman Colosseum", "Taj Mahal"]

    # Print the predicted class
    if predicted_class_index < len(predicted_classes):
        print("Predicted image: ", predicted_classes[predicted_class_index])
    else:
        print("Could not discern image")