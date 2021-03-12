# Isabel Silva
# timeline API 

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
user_db = sqlite.Plugin(dbfile='../userAPI/var/clients.db', keyword='userDB')
app.install(plugin)
app.install(user_db)

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

@get('/users')
def users(userDB):
    all_clients = query(userDB, 'SELECT * FROM users;')

    return {'users':all_clients}

@get('/timeline/<user>')
def getTimeline(user,db,userDB):
    
    #check if user is in userDB 
    try:
        userCheck = query(userDB,'SELECT userName FROM users WHERE userName=?',[user],one=True)
    except sqlite3.IntegrityError as er:
        abort(404, str(er))

    if userCheck is None:
        response.status = 406
        return {'user':userCheck}
    else:
        try:
            userTimeline = query(db, 'SELECT * FROM post WHERE username=? ORDER BY postTimestamp DESC LIMIT 25',[user])
        
        except sqlite3.IntegrityError as er:
            abort(404, str(er))
        response.status=200
        return {'userTimeline':userTimeline}

@get('/timeline/public')
def getPublicTimeline(db):
    # get all the users from user Database 
    try:
        userPosts = query(db, 'SELECT * FROM post ORDER BY postTimestamp DESC LIMIT 25')
    except sqlite3.IntegrityError as er: 
        abort(404,str(er))
    response.status = 200

    return {'usersPosts': userPosts}

@get('/timeline/<user>/home')
def getHomeTimeline(user,db,userDB):
    try:
        userFollows = query(userDB,'SELECT follows FROM userFollows WHERE userName=?',[ user])
    except sqlite3.IntegrityError as er:
        abort(404, str(er))
    posts = []
    user_list = '('
    for i in range(len( userFollows)):
        for k in userFollows[i]:
            if i == len(userFollows)-1:
                user_list += ('\'' + userFollows[i][k] + '\'')
            else:
                user_list += ('\'' + userFollows[i][k] + '\''+',')
    user_list += ')'
    queryStr = 'SELECT * FROM post WHERE userName IN ' + user_list + ' ORDER BY postTimestamp DESC'
    print(queryStr)
    try:
        posts = query(db, queryStr)
    except sqlite3.IntegrityError as er:
        abort(404,str(er))
    response.status = 200
    return {'userFollowPosts':posts}


@post('/timeline/<user>/post/')
def userPost(user,db):
    text = request.json

    if not text:
        abort(400)
    
    posted_fields = text.keys()
    required_fields = {'postText'}

    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields-posted_fields}')
    try: 
      #text = query(db, 'INSERT INTO post(userName,postText,postTimestamp) VALUES (?,?,CURRENT_TIMESTAMP)',[user,text['postText']])
      text['id'] = execute(db,'''
      INSERT INTO post(userName,postText,postTimestamp)
      VALUES (?,?,CURRENT_TIMESTAMP)''', (user,text['postText']))
    except sqlite3.IntegrityError as er: 
        abort(404, str(er))
    response.status = 200
    response.set_header('Location',f"/timeline/{text}")
    
    return {'userPosted':text}

