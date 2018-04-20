import collections
import pprint
import threading
import gevent
from flask import Flask, jsonify, send_from_directory, request, redirect, url_for
from file_read_backwards import FileReadBackwards
from gevent import signal
from gevent.pywsgi import WSGIServer
import error_reporter


class WebConfig:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.wat = ''
        self.wat = ServerThread(self.logger, self.config,
                                self.config.get_config_global('web_config_host_ip'),
                                self.config.get_config_global('web_config_site_port'))

    def start_web_servers(self):
        try:
            self.wat.start()
        except Exception as e:
            self.logger.critical('WebConf', 'The webserver self.config thread ran into an error')
            error_file = error_reporter.print_error_file(e)
            self.logger.error('WebConf', 'Complete stacktrace can be found in {}'.format(error_file))
            self.shutdown_web_servers()

    def shutdown_web_servers(self):
        self.logger.info('WebConf', 'Shutting down the webservers')
        self.wat.join()


class ServerThread(threading.Thread):
    def __init__(self, logger, config, host, port, *args, **kwargs):
        super(ServerThread, self).__init__(*args, **kwargs)
        self.logger = logger
        self.config = config
        self.host = host
        self.port = port
        self.shutdown_fun = self.run

    def run(self):  # Do the actual work.
        app = Flask(__name__)

        def password_is_valid(password):
            if password == self.config.get_config_global('web_password'):
                return True
            return False

        def get_long_argument(arg, group):
            arr = collections.defaultdict(dict)
            for key in arg:
                if key[:len(group)] == group:
                    new_val = arg[key]
                    if arg[key] == 'true':
                        new_val = 1
                    if arg[key] == 'false':
                        new_val = 0
                    arr[key[len(group)+1:-1]] = new_val
            return arr

        def test_item_global(value, key, type_setting, enum=''):
            if type_setting == 'str':
                return self.config.test_global_string(value, key)
            if type_setting == 'int':
                return self.config.test_global_int(value, key)
            if type_setting == 'path':
                return self.config.test_global_path(value, key)
            if type_setting == 'bool':
                return self.config.test_global_or(value, key, [0, 1])
            if type_setting == 'option':
                return self.config.test_global_or(value, key, enum)
            return False

        def test_item_watcher(value, key, type_setting, enum=''):
            if type_setting == 'str':
                return self.config.test_watcher_str(value, key)
            if type_setting == 'int':
                return self.config.test_watcher_int(value, key)
            if type_setting == 'path':
                return self.config.test_watcher_path(value, key)
            if type_setting == 'bool':
                return self.config.test_watcher_boolean(value, key)
            if type_setting == 'option':
                return self.config.test_watcher_or(value, key, enum)
            return False

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
            return jsonify({'data': str(self.host) + ":" + str(self.port)})

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

        @app.route('/global_settings', methods=['GET', 'POST'])
        def get_global_settings():
            if request.method == 'GET':
                args = request.args
                if not password_is_valid(args.get('pass')): return jsonify({'data': 'invalid_pass'})

                items = self.config.get_all_global_settings_json()
                return jsonify(items)

            if request.method == 'POST':
                args = request.form
                if not password_is_valid(args['pass']): return jsonify({'data': 'invalid_pass'})

                all_args = get_long_argument(args, 'global_settings')
                if len(all_args) < 5: return jsonify({'data': 'global_settings_not_specified'})

                pprint.pprint(all_args)
                self.logger.info('WebConfig', 'hoi5')
                for key in all_args:
                    type_setting, possible_enum = self.config.get_config_item_type(key)
                    if type_setting is None and possible_enum is None:
                        return jsonify({'data': 'key_does_not_exist', 'key': key})
                    value = all_args[key]
                    if type_setting == 'int':
                        value = int(all_args[key])
                    if not test_item_global(value, key, type_setting, possible_enum):
                        return jsonify({'data': 'invalid_value', 'key': key})
                    self.config.set_config_global(value, key)

                return jsonify({'data': 'true'})

        @app.route('/all_watcher_settings', methods=['GET'])
        def get_watcher_settings():
            if request.method == 'GET':
                args = request.args
                if not password_is_valid(args['pass']): return jsonify({'data': 'invalid_pass'})

                return jsonify(self.config.get_all_watcher_settings_json())

        @app.route('/watcher_settings/<int:watcher_uid>', methods=['GET', 'POST'])
        def update_watcher_settings(watcher_uid):
            if request.method == 'GET':
                args = request.args
                if not password_is_valid(args['pass']): return jsonify({'data': 'invalid_pass'})

                return self.config.get_all_watcher_settings_json(watcher_uid)

            if request.method == 'POST':
                args = request.form
                if not password_is_valid(args['pass']): return jsonify({'data': 'invalid_pass'})

                all_args = get_long_argument(args, 'watcher_settings')
                if len(all_args) < 5: return jsonify({'data': 'watcher_settings_not_specified'})

                uid = int(watcher_uid)
                if len(self.config.get_watcher_by_uid(uid)) == 0:
                    self.config.add_new_watcher_by_uid(uid)
                for key in all_args:
                    type_setting, possible_enum = self.config.get_config_item_type(key)
                    if type_setting is None and possible_enum is None:
                        return jsonify({'data': 'key_does_not_exist', 'key': key})
                    value = all_args[key]
                    if type_setting == 'int':
                        value = int(all_args[key])
                    if not test_item_watcher(value, key, type_setting, possible_enum):
                        return jsonify({'data': 'invalid_value', 'key': key})
                    self.config.set_config_watcher(uid, value, key)
                self.config.watchers_should_restart(True)
                return jsonify({'data': 'true'})

        @app.route('/remove_watcher/<watcher_uid>', methods=['GET'])
        def remove_watcher(watcher_uid):
            if request.method == 'GET':
                args = request.args
                if not password_is_valid(args['pass']): return jsonify({'data': 'invalid_pass'})

                self.config.remove_watcher(watcher_uid)

                return jsonify({'data': 'true'})

        @app.route('/logging/<end_line>', methods=['GET'])
        def get_logging(end_line):
            if request.method == 'GET':
                args = request.args
                if not password_is_valid(args['pass']): return jsonify({'data': 'invalid_pass'})

                count = 0
                arr = collections.defaultdict(dict)
                with FileReadBackwards(self.config.get_config_global('logging_path'), encoding="utf-8") as frb:
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

        @app.route('/new_file_logging/<end_line>', methods=['GET'])
        def get_new_file_logging(end_line):
            if request.method == 'GET':
                args = request.args
                if not password_is_valid(args['pass']): return jsonify({'data': 'invalid_pass'})

                count = 0
                arr = collections.defaultdict(dict)
                with FileReadBackwards(self.config.get_config_global('logging_path_new_files'), encoding="utf-8")\
                        as frb:
                    for l in frb:
                        if count == int(end_line):
                            if len(arr) < 1:
                                return jsonify({'data': 'end_line_was_0'})
                            return jsonify({'data': arr})
                        split_up = str(l).split(' - ')
                        arr[count]['time'] = split_up[0][:19]
                        arr[count]['config_name'] = split_up[1].strip()
                        split_source = split_up[2].split('/')
                        arr[count]['source_path'] = '/'.join(split_source[:-1]) + '/'
                        arr[count]['filename'] = split_source[-1]
                        arr[count]['destination_path'] = split_up[3]
                        count += 1
                if len(arr) < 1:
                    return jsonify({'data': 'no_lines_in_file'})
                return jsonify({'data': arr})

        self.logger.info('WebConfig', 'Starting host at {}:{}'.format(self.host, self.port))
        try:
            http_server = WSGIServer((self.host, self.port), app)
            self.logger.info('WebConfig', 'Started host {}:{}'.format(self.host, self.port))

            def stop_nicely():
                print('handling signal')
                if http_server.started:
                    http_server.close()

            gevent.signal(signal.SIGTERM, stop_nicely)

            if __name__ == 'webconfig':
                try:
                    http_server.serve_forever()
                except (KeyboardInterrupt, SystemExit):
                    if http_server.started:
                        http_server.stop()
                        self.logger.info('WebConfig', 'Stopped host forcefully')
            else:
                self.logger.critical('WebConfig', 'Error, __name__ is "{}"'.format(__name__))
        except OSError as e:
            self.logger.info('WebConfig', 'Shutdown host {}:{}'.format(self.host, self.port))
            error_file = error_reporter.print_error_file(e)
            self.logger.error('WebConf', 'Complete stacktrace can be found in {}'.format(error_file))
