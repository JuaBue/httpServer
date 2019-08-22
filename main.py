import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT_NUMBER = 8000

# Server paths used to parse the requests
VERSION_LICENSE_PATH = "/version"
SERVER_ROOT_PATH = "/api/v1/"

LICENSE_INFO_PATH = "license"
PUBLIC_KEY_PATH = "server/key"
BORROW_LICENSE_PATH = "license/borrow"
REFRESH_LICENSE_PATH = "license/refresh"
USAGE_LICENSE_PATH = "license/usagereport"
LOGOUT_LICENSE_PATH = "license/logout"

# Response codes
ERROR_SUCCESS = 200
ERROR_BAD_REQUEST = 400
ERROR_UNAUTHORIZED = 401
ERROR_NOT_FOUND = 404
ERROR_INTERNAL = 500

# Get license errors
getLicenseErrors = {ERROR_BAD_REQUEST: ['PARAMETER_MISSING', 'PARAMETER_INVALID', 'AUTH_HEADER_MISSING'],
                    ERROR_UNAUTHORIZED: ['INVALID_CREDENTIALS', 'INVALID_AUTH_CODE'],
                    ERROR_NOT_FOUND: ['LICENSE_NOT_FOUND', 'LICENSE_NOT_AVAILABLE'],
                    ERROR_INTERNAL: ['RETRIEVING_LICENSE_FAILED', 'RETRIEVING_PUBLIC_KEY_FAILED',
                                     'BORROW_LICENSE_FAILED', 'REFRESH_LICENSE_FAILED',
                                     'USAGE_REPORT_FAILED', 'LOGOUT_FAILED']}
getErrorDescription = ['Request does not contain any info', 'Username is missing', 'Password is missing',
                       'MAC address is missing', 'MAC address is invalid:invalid_mac_address', 'Invalid credentials',
                       'License is not configured for user']

passwordReference = ['donno', 'supersecret']

userReference = ['test8', 'john_doe']

class ServerHandler(BaseHTTPRequestHandler):
    request_body = ""
    response_body = ""
    response_code_error = ERROR_INTERNAL
    type_error_index = 0
    error_description = '...'

    def _set_headers(self):
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        return

    def _build_response_body(self, path):
        if path == SERVER_ROOT_PATH + LICENSE_INFO_PATH:
            # Get license information
            if not self._get_error_code():
                self.response_body = {'license': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9'
                                                 '.eyJsaWNlbnNlX3R5cGUiOiJTVEFOREFMT05FIiwibWFjIjoiMDA6RkU6RkE6RkI6Q0Q6RUUiLCJpYXQiOjE1NTk4MjM1OTN9.K03GydhTMNdxUqn_ILpR74hDJqQ71Vcoj-U94ArYhSNMZiQmsf5EfqB_J8KRYa89IiQKgI6LSMLap9TNhXT7R7dF8sHq_lCvt3EwLWH0Po6NgWQrvCfeeCUc6IYjEZQwjSGGuIXJwzyJ9iRufDSn6kBvHY-323f2ErjM1NC10nLe4j4eMrmYXnpy0bY-GIrHKqxFRdOHVG7BQI-S3s2P0t4LdhUwZL9p688FE4-VUaFKp6vbQqITGYhbs7OG6pIKPgYEr56PXMgztEZtc7F-k-0BUMBDgTtOO9dDBxERcw__s0EJ36728dsMAdqtcL__WgooQTrYDRn5tXt6n41TZw'}
        elif path == SERVER_ROOT_PATH + PUBLIC_KEY_PATH:
            # Get public key
            self.response_body = {'public_key': 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAhhTVXMiWgs+l'
                                                '/SvRl0GvAueyLj5bZYu447GpB8HTTu7UG90MQa/YnAx7MsrvLF4mhtp88m8HmJXi/JLbrNF5ur95uDBFrQ29uAvNOuwi0Ohr45dSbkv1+3ExPc8hk1nxhpKVfrIMtTtlzZoxVqiQV5V1Zaj3V02N0INzAQeM3pTRfr1Cgip5DO5kDNwvaeOAkq6JUdictuZzIigajJAngKxUr/6KXp/RYKSN3YjsLeqJ/uY4ggz0TWpnz2wVnR2mrqtAz4os1aToL0Wqrt6hXDix3cL+LlltD9uqci00iH6YATvkk014qZt64c7l0AJRGm7WK/q34D62RY2ZB1UoIwIDAQAB'}
        elif path == SERVER_ROOT_PATH + BORROW_LICENSE_PATH:
            # Borrow license
            self.response_body = {'license': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9'
                                             '.eyJsaWNlbnNlX3R5cGUiOiJGTE9BVElORyIsIm1hYyI6IjAwOkZFOkZBOkZCOkNEOkZGIiwiaWF0IjoxNTU5ODIzNTk2fQ.QuYM-m8-GcadwKPxgD9TV3jvGGy-VYglFEn2O1_3EcE2k4ZzKwXLawP15zdn9oAjPKlC4G1PjCFLHArET1__K65ExiGlPzXiRpXOIz0wC5IxSwerupabvTMr2jKYvR0N3Cct1b_yQcVXua30R_-QvgP4GqDL8sKO2GX8Iq6C1zqGHyHScTPVofj-eJ2KuY0dRq1--A-DIvjA_UcAkHKO7y6zDTSLPT4rlFVR4mm0Ye5eNuMuSY3X4NRa7kCZWy7UHQWPYgU62ARhmyDIV5aQ2wBK_RsHvWJELCveEeVgZcy7z9kE_oRjEbju6Z5w6Jf7zOkySTNSCQN0ZVWlo4e4Hg'}
        elif path == SERVER_ROOT_PATH + REFRESH_LICENSE_PATH:
            # Refresh license
            self.response_body = {'license': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9'
                                             '.eyJsaWNlbnNlX3R5cGUiOiJTVEFOREFMT05FIiwibWFjIjoiMDA6RkU6RkE6RkI6Q0Q6RUUiLCJpYXQiOjE1NTk4MjM1OTN9.K03GydhTMNdxUqn_ILpR74hDJqQ71Vcoj-U94ArYhSNMZiQmsf5EfqB_J8KRYa89IiQKgI6LSMLap9TNhXT7R7dF8sHq_lCvt3EwLWH0Po6NgWQrvCfeeCUc6IYjEZQwjSGGuIXJwzyJ9iRufDSn6kBvHY-323f2ErjM1NC10nLe4j4eMrmYXnpy0bY-GIrHKqxFRdOHVG7BQI-S3s2P0t4LdhUwZL9p688FE4-VUaFKp6vbQqITGYhbs7OG6pIKPgYEr56PXMgztEZtc7F-k-0BUMBDgTtOO9dDBxERcw__s0EJ36728dsMAdqtcL__WgooQTrYDRn5tXt6n41TZw'}
        elif path == SERVER_ROOT_PATH + USAGE_LICENSE_PATH:
            # Report license usage
            self.response_body = ""
        elif path == SERVER_ROOT_PATH + LOGOUT_LICENSE_PATH:
            # Logout license
            self.response_body = ""
        elif path == VERSION_LICENSE_PATH:
            # Get license server version
            self.response_body = "{'app':'License server','version':'1.0.0'}";
        else:
            print("Unknown path: " + path)
            self.response_body = ""

        return self.response_body

    def _send_response(self, code):
        self.send_response(code)
        self._set_headers()
        if self.response_body:
            jsonresponse = json.dumps(self.response_body)
            print(jsonresponse)
            self.wfile.write(jsonresponse.encode('utf-8'))
        return

    def _get_error_code(self):
        self.response_code_error = ERROR_BAD_REQUEST
        self.type_error_index = 0
        if not self.request_body:
            self.error_description = 'Request does not contain any info'
        elif 'username' not in self.request_body:
            self.error_description = 'Username is missing'
        elif self.request_body['username'] == "" or self.request_body['username'] not in userReference:
            self.type_error_index = 1
            self.error_description = 'Username is missing'
        elif 'password' not in self.request_body:
            self.error_description = 'Password is missing'
        elif self.request_body['password'] == "" or self.request_body['password'] not in passwordReference:
            self.type_error_index = 1
            self.error_description = 'Password is missing'
        elif 'mac' not in self.request_body:
            self.error_description = 'MAC address is missing'
        elif self.request_body['mac'] == "" or not re.match('..:..:..:..:..:..', self.request_body['mac']):
            self.type_error_index = 1
            self.error_description = 'MAC address is missing'
        else:
            self.response_code_error = ERROR_SUCCESS
            return False
        self.response_body = {'error': getLicenseErrors[self.response_code_error][self.type_error_index]
            , "error_description": self.error_description}
        return True

    def do_GET(self):
        print("GET request,\nPath: {}\nHeaders:\n{}\n".format(str(self.path), str(self.headers)))
        # Build response
        self.response_body = self._build_response_body(str(self.path))
        # data = {'command': 'GET', 'path': str(self.path)}
        # response_body = json.dumps(data)
        self._send_response(self.response_code_error)
        return

    def do_HEAD(self):
        self._set_headers()
        return

    def do_POST(self):
        self.log_request()
        print("POST\nPath: {}\nHeaders:\n{}\n".format(str(self.path), str(self.headers)))
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        if post_body:
            self.request_body = json.loads(post_body)
            print(self.request_body)
        # Build response
        # data = {'command': 'POST', 'path': str(self.path)}
        # response_body = json.dumps(data)
        self.response_body = self._build_response_body(str(self.path))
        self._send_response(self.response_code_error)
        return


try:
    # Create a web server and define the handler to manage the
    # incoming request
    server = HTTPServer(('', PORT_NUMBER), ServerHandler)
    print('Started http server on port ', PORT_NUMBER)
    # Wait forever for incoming http requests
    server.serve_forever()

except KeyboardInterrupt:
    print('^C received, shutting down the web server')
    server.socket.close()
