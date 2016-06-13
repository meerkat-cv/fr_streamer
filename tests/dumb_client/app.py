import dumb_client
import tornado

if __name__ == '__main__':
    tornado_app = dumb_client.build_app()
    
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        pass
