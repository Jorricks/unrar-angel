import threading
import time
from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
from simplelogger import SimpleLogger
from configer import Config
import json
import ast



class WebConfig:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config

    def start_web_servers(self):
        wat = WebApiThread(self.logger, self.config, self.config.get_config_global('web_config_api_port'))
        sst = StaticServerThread(self.logger, self.config, self.config.get_config_global('web_config_site_port'))
        try:
            wat.start()
            sst.start()
            while True:
                time.sleep(1)
        except:
            self.logger.critical('WebConf', 'The webserver config thread ran into an error')
            wat.join()
            sst.join()


class WebApiThread(threading.Thread):
    def __init__(self, logger, config, port, *args, **kwargs):
        super(WebApiThread, self).__init__(*args, **kwargs)
        self.logger = logger
        self.config = config
        self.port = port

    def run(self):  # Do the actual work.
        app = Flask(__name__)
        api = Api(app)

        parser = reqparse.RequestParser()
        parser.add_argument('global_settings')
        parser.add_argument('watcher_settings')
        parser.add_argument('pass')

        config = self.config

        def password_is_valid(password):
            if password == self.config.get_config_global('web_password'):
                return True
            return False

        def get_long_argument(arg):
            json_text = ast.literal_eval(arg)
            return json.loads(json.dumps(json_text))

        def test_item_global(value, key, type_setting, enum=''):
            if not config.get_config_global(key):
                return False
            if type_setting == 'str':
                return config.test_global_string(value, key)
            if type_setting == 'int':
                return config.test_global_int(value, key)
            if type_setting == 'path':
                return config.test_global_path(value, key)
            if type_setting == 'bool':
                return config.test_global_or(value, key, [0, 1])
            if type_setting == 'or':
                return config.test_global_or(value, key, enum)
            return False

        def test_item_watcher(value, key, type_setting, uid, enum=''):
            if not config.get_config_watcher(uid, key):
                return False
            if type_setting == 'str':
                return config.test_watcher_str(value, key)
            if type_setting == 'int':
                return config.test_watcher_int(value, key)
            if type_setting == 'path':
                return config.test_watcher_path(value, key)
            if type_setting == 'bool':
                return config.test_watcher_boolean(value, key)
            if type_setting == 'or':
                return config.test_watcher_or(value, key, enum)
            return False

        class GlobalSettings(Resource):
            def get(self):
                args = parser.parse_args()
                if not password_is_valid(args['pass']): return jsonify({'data': 'invalid_pass'})

                items = config.get_all_global_settings_json()
                return items

            def post(self):
                args = parser.parse_args()
                if not password_is_valid(args['pass']): return jsonify({'data': 'invalid_pass'})

                if len(args['global_settings']) < 5: return jsonify({'data': 'global_settings_not_specified'})

                all_args = get_long_argument(args['global_settings'])
                for key in all_args:
                    type_setting, possible_enum = config.get_config_item_type(key)
                    if not test_item_global(all_args[key], key, type_setting, possible_enum):
                        return jsonify({'data': 'invalid_key', 'key': key})
                    config.set_config_global(all_args[key], key)

                return jsonify({'data': 'true'})

        class AllWatcherSettings(Resource):
            def get(self):
                args = parser.parse_args()
                if not password_is_valid(args['pass']): return jsonify({'data': 'invalid_pass'})

                return config.get_all_watcher_settings_json()

        class UpdateWatcherSetting(Resource):
            def get(self, watcher_uid):
                args = parser.parse_args()
                if not password_is_valid(args['pass']): return jsonify({'data': 'invalid_pass'})

                return config.get_all_watcher_settings_json(watcher_uid)

            def post(self, watcher_uid):
                args = parser.parse_args()
                if not password_is_valid(args['pass']): return jsonify({'data': 'invalid_pass'})

                if len(args['watcher_settings']) < 5: return jsonify({'data': 'watcher_settings_not_specified'})

                all_args = get_long_argument(args['watcher_settings'])
                uid = int(watcher_uid)
                if len(config.get_watcher_by_uid(uid)) == 0:
                    return jsonify({'data': 'invalid_uid'})
                for key in all_args:
                    type_setting, possible_enum = config.get_config_item_type(key)
                    if not test_item_watcher(all_args[key], key, type_setting, uid, possible_enum):
                        return jsonify({'data': 'invalid_key_or_value', 'key': key})
                    config.set_config_watcher(uid, all_args[key], key)
                    # print('{}, {}'.format(key, all_args['key']))
                    # print('First verify if it is valid. If not, return error.')
                    # print('Second, update the value. Make update calls for this.')
                return jsonify({'data': 'true'})

        api.add_resource(GlobalSettings, '/global_settings')
        api.add_resource(AllWatcherSettings, '/all_watcher_settings')
        api.add_resource(UpdateWatcherSetting, '/watcher_settings/<watcher_uid>')

        if __name__ == '__main__':
            app.run(port=self.port, host='192.168.10.129', debug=True, use_reloader=False)


class StaticServerThread(threading.Thread):
    def __init__(self, logger, config, port, *args, **kwargs):
        super(StaticServerThread, self).__init__(*args, **kwargs)
        self.logger = logger
        self.config = config
        self.port = port

    def run(self):  # Do the actual work.
        app = Flask(__name__)
        api = Api(app)

        class HelloWorld(Resource):
            def get(self):
                return {'hello': 'world'}

        api.add_resource(HelloWorld, '/')

        if __name__ == '__main__':
            app.run(port=self.port, debug=True, use_reloader=False)


webconf = WebConfig(SimpleLogger('DEBUG', '/tmp/angel-logger.log'), Config())
webconf.start_web_servers()
