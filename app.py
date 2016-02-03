import fr_on_premise
import tornado

if __name__ == '__main__':
    tornado_app = fr_on_premise.build_app()
    tornado_app.listen(4443)

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        pass
