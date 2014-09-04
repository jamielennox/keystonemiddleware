# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

ENV_KEY = 'wsgi.keystonemiddleware.auth_location'


class AuthLocation(object):

    def __init__(self, app, config):
        self._app = app
        self._location = config.get('auth_uri')

    def __call__(self, env, start_response):
        env[ENV_KEY] = self._location

        if not self._location:
            return self._app(env, start_response)

        def _fake_start_response(status, response_headers, exc_info=None):
            if status.startswith('401'):
                msg = "Keystone uri='%s'" % self._location
                response_headers.append(('WWW-Authenticate', msg))

            return start_response(status, response_headers, exc_info)

        return self._app(env, _fake_start_response)


if __name__ == '__main__':
    """Run this module directly to start a protected echo service::

        $ python -m keystonemiddleware.auth_location

    """
    # def echo_app(environ, start_response):
    #     """A WSGI application that echoes the CGI environment to the user."""
    #     start_response('200 OK', [('Content-Type', 'application/json')])
    #     environment = dict((k, v) for k, v in six.iteritems(environ)
    #                        if k.startswith('HTTP_X_'))
    #     yield jsonutils.dumps(environment)

    from webob import dec
    import webob
    from wsgiref import simple_server

    @dec.wsgify
    def simple_app(req):
        r = webob.Response(body='test',
                           # status='401 Unauthorized',
                           status='200 OK',
                           content_type='application/text')

        r.headers['header-a'] = 'is a'
        return r


    # hardcode any non-default configuration here
    conf = {'auth_uri': 'http://myurl'}
    app = AuthLocation(simple_app, conf)
    server = simple_server.make_server('', 8000, app)
    print('Serving on port 8000 (Ctrl+C to end)...')
    server.serve_forever()
