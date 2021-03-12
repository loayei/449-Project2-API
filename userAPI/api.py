# Isabel Silva
# users 

import sys
import textwrap
import logging.config
import sqlite3

import bottle
from bottle import * 
from bottle.ext import sqlite

# SET UP 
app = bottle.default_app()
app.config.load_config('./etc/api.ini')

plugin = sqlite.Plugin(app.config['sqlite.dbfile'])
app.install(plugin)

logging.config.fileConfig(app.config['logging.config'])


# RETURN errors in JSON 
def json_error_handler(res):
    if res.content_type == 'application/json':
        return res.body
    res.content_type = 'application/json'
    if res.body == 'Unknown Error.':
        res.body = bottle.HTTP_CODES[res.status_code]
    return bottle.json_dumps({'error': res.body})

# DISABLE warning produced by BOTTLE 
if not sys.warnoptions:
    import warnings
    for warning in [DeprecationWarning, ResourceWarning]:
        warnings.simplefilter('ignore', warning)
# Simplify DB ACCESS
def query(db, sql, args=(), one=False):
    cur = db.execute(sql, args)
    rv = [dict((cur.description[idx][0], value)
          for idx, value in enumerate(row))
          for row in cur.fetchall()]
    cur.close()

    return (rv[0] if rv else None) if one else rv


def execute(db, sql, args=()):
    cur = db.execute(sql, args)
    id = cur.lastrowid
    cur.close()

    return id

# ROUTES

@get('/')
def home(): 
    return textwrap.dedent('''
    <h1>Isabel Silva Proj1 Client Contract</h1>\n''')

@get('/users')
def users(db):
    all_clients = query(db, 'SELECT * FROM users;')

    return {'users':all_clients}

# create new user
@post('/users/')
def create_user(db):
    user = request.json

    if not user:
        abort(400)

    posted_fields = user.keys()
    required_fields = {'userName','email','pswd'}

    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields - posted_fields}')
    
    try:
        user['id'] = execute(db,'''
        INSERT INTO users(userName, email, pswd) VALUES
        (:userName, :email, :pswd)
        ''', user)

    except sqlite3.IntegrityError as e:
        abort(409, str(e))

    response.status = 201
    response.set_header('Location',f"/users/{user['id']}")
    return user

# check password?? 
@post('/users/<user>/pcheck/')
def check_password(user,db):
    data = request.json
   
    check = None 

    if not data:
        abort(400)
    
    posted_fields = data.keys()
    required_fields = {'pswd'}

    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields - posted_fields}')


    try: 
        #check['userName'] = execute(db, 'SELECT * FROM users WHERE userName=? AND pswd=?', (user,data['pswd']))
        check = query(db,'SELECT * FROM users WHERE userName=? AND pswd=?',[user, data['pswd']], one=True)
        if not user:
            abort(404)
        
    except sqlite3.IntegrityError as er: 
        abort(404, str(er))
    if check is None:
        response.status = 406
        return {'users':check}
    else:
        response.status = 200
        response.set_header('location',f"/user/pswdcheck") 
        return {'users':check}

# view user's followers 
@get ('/users/follows/<user>')
def view_followings(user,db):
    follow_all = query(db, 'SELECT follows  FROM userFollows WHERE userName = ?', [user])
    if not follow_all:
        abort(404)
    return {'userFollows': follow_all}

# add a new follower 
@post('/users/<user>/follow/')
def add_follower(user,db):
    data = request.json
    addFollower = None
    if not data:
        abort(400)
    posted_fields = data.keys()
    required_fields = {'follows'}

    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields - posted_fields}')
    
    try:
        #data['id'] = execute(db, ''' 
        #INSERT INTO userFollows(userName, follows) VALUES (
        #:userName, :follows)''', data)
        addFollower = query(db, 'INSERT INTO userFollows(userName, follows) VALUES (?, ?)',[user, data['follows']])
    except sqlite3.IntegrityError as e: 
        abort(409, str(e))

    response.status = 201
    #response.set_header('Location',f"/user/{data['id']}")
    return {'addFollower': data}

# delete following 
@delete('/users/delete/')
def delete_follow(db):
    data =request.json

    if not data: 
        abort(400)
    posted_fields = data.keys()
    required_fields = {'userName','follows'}
    
    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields - posted_fields}')

    try:
        data['id'] = execute(db,'''
           DELETE FROM userFollows WHERE userName = :userName AND
           follows = :follows''', data)
    except sqlite.IntegrityError as e: 
        abort(409, str(e))
    
    response.status = 200
    response.set_header('Location',f"/users/delete/{data['id']}")
    return data


