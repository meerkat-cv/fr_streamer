import tornado
import numpy as np
import cv2
import frame_pb2
import tornado.websocket 
import tornado.speedups

PORT = 8000

class EchoWebSocket(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        pass
        print("mes")
        # frame = np.frombuffer(message, dtype=np.uint8)
        # frame = cv2.imdecode(frame, cv2.IMWRITE_JPEG_QUALITY)
        # cv2.imshow("frame", frame)
        # cv2.waitKey(10)
        
    def on_close(self):
        print("WebSocket closed")


application = tornado.web.Application(
    [
        (r"/echo", EchoWebSocket),
    ]
)
 
if __name__ == "__main__":
    application.listen(PORT)
    print("Running app on port {}".format(PORT))
    tornado.ioloop.IOLoop.instance().start()
        # message = ws.receive()
        # print('message!', message)
        # f = frame_pb2.ParseFromString(message)
        # print(f)


        # arr = np.asarray(bytearray(message), dtype=np.uint8)
        # arr = np.reshape(arr, (256,256))
        # print(arr)
        # image = arr
        # #cv2.imdecode(arr, cv2.CV_LOAD_IMAGE_GRAYSCALE)
        # height, width = image.shape[:2]
        # print(height)
        # print(width)
        # cv2.imwrite('received.jpg', image)

        # # cv2.waitKey()
        # print('written.')
        # ws.send("I received this")

