import os
import sys

def parse_pgpass(pgpass_file=None, host=None, port=None, dbname=None, user=None, password=None):
    _host, _port, _dbname, _user, _password = host, port, dbname, user, password
    if _host is None or _port is None or _dbname is None or _user is None or _password is None:
        if pgpass_file is None:
            raise ValueError("If 'host', 'port', 'dbname', 'user' or 'password' is None, "
                             "then 'pgpass_file' must not be None.")
        else:
            pgpass = os.path.expanduser(pgpass_file)
            if sys.platform.startswith('win') and pgpass_file == '~/.pgpass':
                # Fix passfile location for Windows
                pgpass = pgpass.replace('/', os.sep)
                if not os.path.isfile(pgpass):
                    if os.path.isfile(pgpass.replace(os.sep+'.', os.sep)):
                        pgpass = pgpass.replace(os.sep+'.', os.sep)
            if not os.path.isfile(pgpass):
                raise FileNotFoundError('pgpass file {!r} not found.'.format(pgpass))
            with open(pgpass, encoding="utf-8") as f:
                for line in f:
                    line_split = line.rstrip().split(':')
                    if line.startswith('#') or len(line_split) != 5:
                        continue
                    f_host, f_port, f_dbname, f_user, f_password = line_split

                    _host = f_host
                    if host is None:
                        if f_host == '*':
                            continue
                    elif f_host in {'*', host}:
                        _host = host
                    else:
                        continue

                    _port = f_port
                    if port is None:
                        if f_port == '*':
                            continue
                    elif f_port in {'*', port}:
                        _port = port
                    else:
                        continue

                    _dbname = f_dbname
                    if dbname is None:
                        if f_dbname == '*':
                            continue
                    elif f_dbname in {'*', dbname}:
                        _dbname = dbname
                    else:
                        continue

                    _user = f_user
                    if user is None:
                        if f_user == '*':
                            continue
                    elif f_user in {'*', user}:
                        _user = user
                    else:
                        continue

                    password = password or f_password
                    break

    if password is None:
        raise ValueError(('no password found for '
                          'host: {}, port: {}, dbname: {}, user: {}'
                          ).format(host, port, dbname, user))
    else:
        _password = password
    return {'host': _host, 'port': _port, 'dbname': _dbname, 'user': _user, 'password': _password}
