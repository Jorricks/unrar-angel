import collections
import threading
import json
import ast
from flask import Flask, jsonify, send_from_directory, request, redirect, url_for
from flask_cors import CORS
from flask_restful import Resource, Api, reqparse
from werkzeug.serving import make_server
from file_read_backwards import FileReadBackwards


class WebConfig:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.wat = ''
        self.sst = ''

    def start_web_servers(self):
        self.wat = WebApiThread(self.logger, self.config,
                                self.config.get_config_global('web_config_host_ip'),
                                self.config.get_config_global('web_config_api_port'))
        self.sst = StaticServerThread(self.logger, self.config,
                                      self.config.get_config_global('web_config_host_ip'),
                                      self.config.get_config_global('web_config_site_port'))
        try:
            self.wat.start()
            self.sst.start()
        except:
            self.logger.critical('WebConf', 'The webserver config thread ran into an error')
            self.shutdown_web_servers()
            self.wat.shutdown_server()
            self.sst.shutdown_server()
            self.wat.join()
            self.sst.join()

    def shutdown_web_servers(self):
        self.logger.info('WebConf', 'Shutting down the webservers')
        self.wat.shutdown_server()
        self.sst.shutdown_server()
        self.wat.join()
        self.sst.join()


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

        self.logger.info('WebConfig', 'Starting host at {}:{}'.format(self.host, self.port))
        try:
            self.srv = make_server(self.host, self.port, app)
            self.logger.info('WebConfig', 'Started host {}:{}'.format(self.host, self.port))
        except OSError as e:
            self.logger.info('WebConfig', 'Error starting host {}:{}'.format(self.host, self.port))
            self.logger.info('WebConfig', '{}'.format(e))
        if __name__ == 'webconfig':
            self.srv.serve_forever()
        else:
            self.logger.critical('WebConfig', 'Error, __name__ is "{}"'.format(__name__))

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

        @app.route('/')
        def index():
            password = request.cookies.get('password')
            if password == self.config.get_config_global('web_password'):
                return send_from_directory('web-config/config/', 'index.html')
            else:
                return redirect(url_for('login'))

        @app.route('/login')
        def login():
            return send_from_directory('web-config/login/', 'index.html')

        @app.route('/favicon.ico')
        def get_favicon():
            return send_from_directory('', 'favicon.ico')

        @app.route('/get_api_info')
        def get_api_info():
            return jsonify({'data': str(self.host) + ":" + str(self.config.get_config_global('web_config_api_port'))})

        @app.route('/is_valid_pass/<string:string>')
        def is_valid_pass(string):
            if string == self.config.get_config_global('web_password'):
                return jsonify({'data': 'valid'})
            else:
                return jsonify({'data': 'invalid'})

        # resp = make_response(send_from_directory('web-config/login/', 'index.html'))
        # resp.set_cookie('password', expires=0)
        # return resp

        @app.route('/config/js/<path:path>')
        def send_config_js(path):
            return send_from_directory('web-config/config/js', path)

        @app.route('/config/css/<path:path>')
        def send_config_css(path):
            return send_from_directory('web-config/config/css', path)

        @app.route('/config/img/<path:path>')
        def send_config_img(path):
            return send_from_directory('web-config/config/img', path)

        @app.route('/login/js/<path:path>')
        def send_login_js(path):
            return send_from_directory('web-config/login/js', path)

        @app.route('/login/css/<path:path>')
        def send_login_css(path):
            return send_from_directory('web-config/login/css', path)

        self.logger.info('WebConfig', 'Starting host at {}:{}'.format(self.host, self.port))
        try:
            self.srv = make_server(self.host, self.port, app)
            self.logger.info('WebConfig', 'Started host {}:{}'.format(self.host, self.port))
        except OSError as e:
            self.logger.info('WebConfig', 'Error starting host {}:{}'.format(self.host, self.port))
            self.logger.info('WebConfig', '{}'.format(e))

        if __name__ == 'webconfig':
            self.srv.serve_forever()
        else:
            self.logger.critical('WebConfig', 'Error, __name__ is "{}"'.format(__name__))

    def shutdown_server(self):
        self.srv.shutdown()
