import fr_streamer
import tornado

if __name__ == '__main__':
    tornado_app = fr_streamer.build_app()
    tornado_app.listen(4443)

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        pass
