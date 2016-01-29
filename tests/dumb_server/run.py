from flask import Flask
from flask import request
import cv2
import numpy as np
app = Flask(__name__)


def read_cvimage_from_stream(stream):
    try:
        arr = np.asarray(bytearray(stream.read()), dtype=np.uint8)
        image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        height, width = image.shape[:2]
        if height <= 0 or width <= 0:
            raise Exception('Invalid image file from stream')
    except:
        raise Exception('Invalid image file from stream')

    return image


def parse_content_type(content_type):
    """
    This function is used to extract the content type from the header.
    """
    json_type = 'application/json'
    data_type = 'multipart/form-data'
    lower_content_type = content_type.lower()

    if lower_content_type.find(json_type) >= 0:
        return json_type
    elif lower_content_type.find(data_type) >= 0:
        return data_type
    else:
        abort(415)


@app.route("/test_premise_post", methods=['POST'])
def hello():
    content_type = parse_content_type(request.headers['content-type'])
    if content_type == 'application/json':
        print('Received from recognition', request.get_json(True))
    elif content_type == 'multipart/form-data':
        if 'image' in request.files:
            image = read_cvimage_from_stream(request.files['image'])
            cv2.imwrite('last_recognition.jpg', image)
            print('Image saved at last_recognition.png')
        if 'recognition' in request.files:
            print('Recognition data:', request.files['recognition']);
    
    return "Ok!"

if __name__ == "__main__":
    app.run(debug=True)