import os
import re
import time
import html
import base64
import pickle
import subprocess
import urllib.request
import urllib.parse as urlparse


class Attack():
    def __init__(self, title, description, route, good_path, evil_path, reference):
        self.title = title
        self.description = description
        self.route = route
        self.good_path = good_path
        self.evil_path = evil_path
        self.reference = reference

    def run(self):
        pass


class SQLinjection(Attack):
    def run(self, handler):
        params = handler.params
        cursor = handler.server.connection.cursor()

        id = '9999999' if 'id' not in params else params['id'][0]
        cursor.execute("SELECT id, username, name, surname, session FROM users WHERE id=" + id)

        rows = ""
        for row in cursor.fetchall():
            columns = ""
            for column in row:
                columns += "".join("<td>{}</td>".format("-" if column is None else column))
            rows += "".join("<tr>{}</tr>".format(columns))

        content = """
            <h2>Result(s):</h2>
            <table class="table">
                <thead>
                    <th scope="col">ID</th>
                    <th scope="col">Username</th>
                    <th scope="col">Name</th>
                    <th scope="col">Surname</th>
                    <th scope="col">Session</th>
                </thead>
                {}
            </table>
        """.format(rows)

        return content


class XSSReflected(Attack):
    def run(self, handler):
        params = handler.params

        content = params.get('msg', '')
        if len(content):
            content = content[0]
        else:
            content = 'No messages...'

        return content


class XSSStored(Attack):
    def run(self, handler):
        params = handler.params
        connection = handler.server.connection
        cursor = connection.cursor()

        if 'comment' in params:
            comment = params.get('comment', '')[0]
            cursor.execute('INSERT INTO comments VALUES(NULL, ?, ?)', [comment, time.ctime()])
            connection.commit()
            content = 'Thank you for leaving the comment. Please click <a href=/guestbook?comment=>here</a> to see all comments...'
        else:
            cursor.execute("SELECT id, comment, time FROM comments")
            rows = ""
            for row in cursor.fetchall():
                columns = ""
                for column in row:
                    columns += "".join("<td>{}</td>".format("-" if column is None else column))
                rows += "".join("<tr>{}</tr>".format(columns))

            content = '''
                <div><span>Comment(s):</span></div>
                <table>
                    <thead>
                        <th>id</th>
                        <th>comment</th>
                        <th>time</th>
                    </thead>
                    {}
                </table>'''.format(rows)

        return content


class UnvalidatedRedirect(Attack):
    def run(self, handler):
        params = handler.params

        path = params.get('path', '/')[0]
        content = '''
            <script>
                setTimeout(function() {{
                    window.location.replace('{path}');
                }}, 3000);
            </script>
        '''.format(path=path)

        return content


class ExecutionAfterRedirect(Attack):
    def run(self, handler):
        cookie = handler.cookie

        content = '''
            <ul>
                <li><a href=#>Manage Users</a></li>
                <li><a href=#>Update Database Settings</a></li>
            </ul>
        '''

        if not cookie:
            content += "<script>window.location = '/login';</script>"

        return content


class CommandInjection(Attack):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        domain = 'www.google.com'
        payload = ';ifconfig' if os.name != 'nt' else '&ipconfig'
        payload = urlparse.quote_plus(payload)
        self.evil_path = '{}?domain={}{}'.format(self.route, domain, payload)

    def run(self, handler):
        params = handler.params

        content = 'Try <a href="{}">this</a> or <a href="{}">this</a>...'.format(self.good_path, self.evil_path)
        if 'domain' in params:
            command = 'host' if os.name != 'nt' else 'nslookup'
            domain = params.get('domain', '/')[0]
            output = subprocess.check_output(
                ' '.join([command, domain]),
                shell=True,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE
            )
            content = '<pre>{}</pre>'.format(output.decode())

        return content


class UnsafeDeserialization(Attack):

    class RCE:
        def __reduce__(self):
            cmd = ('whoami >> poc.txt')
            return os.system, (cmd,)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        payload = base64.urlsafe_b64encode(pickle.dumps(dict(one=1, two=2, three=3))).decode()
        self.good_path = '/extract?object={}'.format(payload)
        payload = base64.urlsafe_b64encode(pickle.dumps(self.RCE())).decode()
        self.evil_path = '/extract?object={}'.format(payload)

    def run(self, handler):
        params = handler.params

        content = 'Try <a href="{}">this</a> or <a href="{}">this</a>...'.format(self.good_path, self.evil_path)

        if 'object' in params:
            object = params.get('object', '')[0]
            content = str(pickle.loads(base64.urlsafe_b64decode(object)))

        return content


class PathTraversal(Attack):
    def run(self, handler):
        params = handler.params

        try:
            path = params.get('path', ['docs/cursus.txt'])[0]
            if '://' not in path:
                file = open(os.path.abspath(path), 'rb')
            else:
                file = urllib.request.urlopen(path)

            file = html.escape(file.read().decode())
        except:
            file = 'File not found...'

        content = '<pre><code>{}</code></pre>'.format(file)

        return content


class SessionFixation(Attack):
    def run(self, handler):
        params = handler.params
        cookie = handler.cookie

        if params.keys() & {'session'}:
            session = params.get('session')[0]
            cookie['SESSIONID'] = session

        path = params.get('path', '/')[0]
        content = '''
            <script>
                setTimeout(function() {{
                    window.location = '{path}';
                }}, 3000);
            </script>
        '''.format(path=path)

        return content


class SessionHijacking(Attack):
    def run(self, handler):
        cursor = handler.server.connection.cursor()
        session = handler.cookie['SESSIONID'].value

        cursor.execute("SELECT * FROM users WHERE session = ?", [session])
        user = cursor.fetchone()
        if user:
            content = 'Welcome <strong>{} {}</strong>!'.format(user[2], user[3])
        else:
            content = 'Please login, <strong>Anonymous</strong>!'

        return content


class AuthBypass(Attack):
    def run(self, handler):
        params = handler.params
        connection = handler.server.connection
        cursor = connection.cursor()
        session = handler.cookie['SESSIONID'].value

        type = 'empty'
        message = ''
        content = '''
            <div class="alert alert-{type}" role="alert">
                <div class="message">{message}</div>
            </div>
        '''

        if params.keys() == {'username', 'password'}:
            username = re.sub(r"[^\w]", '', params.get('username')[0])
            password = params.get('password')[0]

            cursor.execute("SELECT * FROM users WHERE username='" +  username + "' AND password='" + password + "'")
            user = cursor.fetchone()
            if user:
                type = 'success'
                message = 'Welcome <strong>{} {}</strong>!'.format(user[2], user[3])
                cursor.execute("UPDATE users SET session = ? WHERE id = ?", (session, user[0]))
                connection.commit()
            else:
                type = 'danger'
                message = 'The username and/or password is incorrect!'

        content = content.format(type=type, message=message)

        return content