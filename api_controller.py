from dovecot import Dovecot
from exim import Exim
import os, configparser, logging, random, string
from flask import Flask, json, request, jsonify


config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

log_file = os.path.join(os.path.dirname(__file__), config['logging']['log_file_path'])

if os.path.isfile(log_file):
    logging.basicConfig(filename=log_file, level=logging.DEBUG, filemode='a', datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s - %(name)s - %(levelname)-8s: %(message)s')
else:
    f = open(log_file, "x")
    f.write("Log file has been initialized...\n")
    f.close()
    logging.basicConfig(filename=log_file, level=logging.WARNING, filemode='a', datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s - %(name)s - %(levelname)-8s: %(message)s')



class ApiController:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
        self.__dovecot = Dovecot()
        self.__exim = Exim()
        letters = string.ascii_letters
        result_str = ''.join(random.choice(letters) for i in range(20))
        self.__username = config['api']['username']
        self.__password = config['api']['password']
        self.__token = result_str


    def dovecot_brute_force(self):
        self.__dovecot.brute_force()

    def dovecot_suspicious_login(self):
        self.__dovecot.suspicious_login()

    def exim_sending_rate(self):
        self.__exim.sending_rate()

    def exim_brute_force(self):
        self.__exim.brute_force()

    def validate_token(self, token):
        if self.__token == token:
            return True
        return False

    def create_token(self):
        letters = string.ascii_letters
        result_str = ''.join(random.choice(letters) for i in range(20))
        self.__token = result_str
        return self.__token

    def validate_credentials(self, username, password):
        if username == self.__username and password == self.__password:
            return True
        return False


api = Flask(__name__)
api.config["DEBUG"] = True

api_controller = ApiController()

@api.route('/token', methods=['GET'])
def get_token():
    if 'usr' in request.args and 'pwd' in request.args:
        if api_controller.validate_credentials(request.args['usr'], request.args['pwd']):
            return api_controller.create_token()
        return "[Error] Please retry with another credentials..."
    return "[Error] Please retry with another parameters..."

@api.route('/dovecot', methods=['GET'])
def get_dovecot():
    if 'token' in request.args and 'type' in request.args and api_controller.validate_token(request.args['token']):
        if request.args['type'] == 'susp':
            api_controller.dovecot_suspicious_login()
            return 'Dovecot [Suspicious Login] analysis was finished successfully!'
        elif request.args['type'] == 'brute':
            api_controller.dovecot_brute_force()
            return 'Dovecot [Brute Force] analysis was finished successfully!'
        return "[Error] Please retry with another type..."
    return "[Error] Please retry with another parameters..."


@api.route('/exim', methods=['GET'])
def get_exim():
    if 'token' in request.args and 'type' in request.args and api_controller.validate_token(request.args['token']):
            if request.args['type'] == 'susp':
                api_controller.exim_sending_rate()
                return 'Exim [Sending Rate] analysis was finished successfully!'
            if request.args['type'] == 'brute':
                api_controller.exim_brute_force()
                return 'Exim [Brute Force] analysis was finished successfully!'
            return "[Error] Please retry with another type..."
    return "[Error] Please retry with another parameters..."


if __name__ == '__main__':
    #api.run()
    controller = ApiController()
    controller.exim_brute_force()
