import threading, time
from flask import Flask
from flask_restful import Resource, Api


class WebConfig():
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config

    def start_web_server(self):
        try:
            WebServerThread(self.logger, self.config).start()
        except:
            t.join()
            self.logger.critical('WebConf', 'The webserver config thread ran into an error')


class WebServerThread(threading.Thread):
    def __init__(self, logger, config, *args, **kwargs):
        super(WebServerThread,self).__init__(*args, **kwargs)
        self.logger = logger
        self.config = config

    def run(self):  # Do the actual work.
        app = Flask(__name__)
        api = Api(app)

        class HelloWorld(Resource):
            def get(self):
                return {'hello': 'world'}

        api.add_resource(HelloWorld, '/')

        if __name__ == '__main__':
            app.run(debug=True)
        app.run(debug=True)
