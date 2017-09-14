import collections
import threading
import time
import json
import ast
from flask import Flask, jsonify
from flask_cors import CORS
from flask_restful import Resource, Api, reqparse
from werkzeug.serving import make_server
from file_read_backwards import FileReadBackwards
from simplelogger import SimpleLogger
from configer import Config


class WebConfig:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config

    def start_web_servers(self):
        wat = WebApiThread(self.logger, self.config,
                           self.config.get_config_global('web_config_host_ip'),
                           self.config.get_config_global('web_config_api_port'))
        sst = StaticServerThread(self.logger, self.config,
                                 self.config.get_config_global('web_config_host_ip'),
                                 self.config.get_config_global('web_config_site_port'))
        try:
            wat.start()
            sst.start()
            while True:
                time.sleep(1)
        except:
            self.logger.critical('WebConf', 'The webserver config thread ran into an error')
            wat.shutdown_server()
            sst.shutdown_server()
            wat.join()
            sst.join()


class WebApiThread(threading.Thread):
    def __init__(self, logger, config, host, port, *args, **kwargs):
        super(WebApiThread, self).__init__(*args, **kwargs)
        self.logger = logger
        self.config = config
        self.host = host
        self.port = port
        self.shutdown_fun = self.run
        self.srv = ''

    def run(self):  # Do the actual work.
        app = Flask(__name__)
        CORS(app)
        api = Api(app)

        parser = reqparse.RequestParser()
        parser.add_argument('global_settings')
        parser.add_argument('watcher_settings')
        parser.add_argument('pass')

        config = self.config

        def password_is_valid(password):
            if password == config.get_config_global('web_password'):
                return True
            return False

        def get_long_argument(arg):
            json_text = ast.literal_eval(arg)
            return json.loads(json.dumps(json_text))

        def test_item_global(value, key, type_setting, enum=''):
            if type_setting == 'str':
                return config.test_global_string(value, key)
            if type_setting == 'int':
                return config.test_global_int(value, key)
            if type_setting == 'path':
                return config.test_global_path(value, key)
            if type_setting == 'bool':
                return config.test_global_or(value, key, [0, 1])
            if type_setting == 'option':
                return config.test_global_or(value, key, enum)
            return False

        def test_item_watcher(value, key, type_setting, uid, enum=''):
            if type_setting == 'str':
                return config.test_watcher_str(value, key)
            if type_setting == 'int':
                return config.test_watcher_int(value, key)
            if type_setting == 'path':
                return config.test_watcher_path(value, key)
            if type_setting == 'bool':
                return config.test_watcher_boolean(value, key)
            if type_setting == 'option':
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
                print(args['pass'])
                print(args['pass'])
                if not password_is_valid(args['pass']): return jsonify({'data': 'invalid_pass'})

                if len(args['global_settings']) < 5: return jsonify({'data': 'global_settings_not_specified'})

                all_args = get_long_argument(args['global_settings'])
                for key in all_args:
                    type_setting, possible_enum = config.get_config_item_type(key)
                    if type_setting is None and possible_enum is None:
                        return jsonify({'data': 'key_does_not_exist', 'key': key})
                    value = all_args[key]
                    if type_setting == 'int':
                        value = int(all_args[key])
                    if not test_item_global(value, key, type_setting, possible_enum):
                        return jsonify({'data': 'invalid_value', 'key': key})
                    config.set_config_global(value, key)

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
                    config.add_new_watcher_by_uid(uid)
                for key in all_args:
                    type_setting, possible_enum = config.get_config_item_type(key)
                    if type_setting is None and possible_enum is None:
                        return jsonify({'data': 'key_does_not_exist', 'key': key})
                    value = all_args[key]
                    if type_setting == 'int':
                        value = int(all_args[key])
                    if not test_item_watcher(value, key, type_setting, uid, possible_enum):
                        return jsonify({'data': 'invalid_value', 'key': key})
                    config.set_config_watcher(uid, value, key)
                return jsonify({'data': 'true'})

        class RemoveWatcher(Resource):
            def get(self, watcher_uid):
                args = parser.parse_args()
                if not password_is_valid(args['pass']): return jsonify({'data': 'invalid_pass'})

                config.remove_watcher(watcher_uid)

                return jsonify({'data': 'true'})

        class LoggingInfo(Resource):
            def get(self, end_line):
                args = parser.parse_args()
                if not password_is_valid(args['pass']): return jsonify({'data': 'invalid_pass'})

                count = 0
                arr = collections.defaultdict(dict)
                with FileReadBackwards(config.get_config_global('logging_path'), encoding="utf-8") as frb:
                    for l in frb:
                        if count == int(end_line):
                            if len(arr) < 1:
                                return jsonify({'data': 'end_line_was_0'})
                            return jsonify({'data': arr})
                        split_up = str(l).split(' - ')
                        arr[count]['time'] = split_up[0][:19]
                        arr[count]['level'] = split_up[1].title().strip()
                        arr[count]['component'] = split_up[2].title().strip()
                        arr[count]['message'] = split_up[3]
                        count += 1
                if len(arr) < 1:
                    return jsonify({'data': 'no_lines_in_file'})
                return jsonify({'data': arr})

        class NewFileLogging(Resource):
            def get(self, end_line):
                args = parser.parse_args()
                if not password_is_valid(args['pass']): return jsonify({'data': 'invalid_pass'})

                count = 0
                arr = collections.defaultdict(dict)
                with FileReadBackwards(config.get_config_global('logging_path_new_files'), encoding="utf-8") as frb:
                    for l in frb:
                        if count == int(end_line):
                            if len(arr) < 1:
                                return jsonify({'data': 'end_line_was_0'})
                            return jsonify({'data': arr})
                        split_up = str(l).split(' - ')
                        arr[count]['time'] = split_up[0][:19]
                        arr[count]['config_name'] = split_up[1].strip()
                        split_source = split_up[2].split('/')
                        arr[count]['source_path'] = '/'.join(split_source[:-1])+'/'
                        arr[count]['filename'] = split_source[-1]
                        arr[count]['destination_path'] = split_up[3]
                        count += 1
                if len(arr) < 1:
                    return jsonify({'data': 'no_lines_in_file'})
                return jsonify({'data': arr})

        api.add_resource(GlobalSettings, '/global_settings')
        api.add_resource(AllWatcherSettings, '/all_watcher_settings')
        api.add_resource(UpdateWatcherSetting, '/watcher_settings/<watcher_uid>')
        api.add_resource(RemoveWatcher, '/remove_watcher/<watcher_uid>')
        api.add_resource(LoggingInfo, '/logging/<end_line>')
        api.add_resource(NewFileLogging, '/new_file_logging/<end_line>')

        self.srv = make_server(self.host, self.port, app)

        if __name__ == '__main__':
            self.srv.serve_forever()

    def shutdown_server(self):
        self.srv.shutdown()


class StaticServerThread(threading.Thread):
    def __init__(self, logger, config, host, port, *args, **kwargs):
        super(StaticServerThread, self).__init__(*args, **kwargs)
        self.logger = logger
        self.config = config
        self.host = host
        self.port = port
        self.shutdown_fun = self.run
        self.srv = ''

    def run(self):  # Do the actual work.
        app = Flask(__name__)
        api = Api(app)

        class HelloWorld(Resource):
            def get(self):
                return {'hello': 'world'}

        api.add_resource(HelloWorld, '/')

        self.srv = make_server(self.host, self.port, app)
        if __name__ == '__main__':
            self.srv.serve_forever()

    def shutdown_server(self):
        self.srv.shutdown()

webconf = WebConfig(SimpleLogger('DEBUG', '/tmp/angel-logger.log', '/tmp/angel-logger-new-files.log'), Config())
webconf.start_web_servers()
