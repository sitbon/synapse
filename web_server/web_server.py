import os
import json
from bottle import route, request, run, template, static_file
from pysqlite2 import dbapi2 as sqlite3

@route('/')
@route('/index')
def index():
    return template('index.tpl')

@route('/data/proximity', method='POST')
def post_proximity():
    val = request.POST.get('value', -1)

    if val != -1:
        # put in db
        db = sqlite3.connect('./dress.db')
        c = db.cursor()
        c.execute("INSERT INTO proximity (value) VALUES (?)", (val,))
        db.commit()
        row_id = c.lastrowid

        c.close()

        return {"success" : True, "id" : row_id}
    else:
        # error
        return {"success" : False, "error" : "No data supplied"}

@route('/data/proximity/<item>')
def proximity_data(item):
    db = sqlite3.connect('./dress.db')
    c = db.cursor()
    c.execute("SELECT * FROM proximity WHERE id > ?", (item,))
    rows = c.fetchall()
    rows_list = []

    c.close()

    if rows:
        for row in rows:
            t = (row[0], row[1])
            rows_list.append(t)
        return {"success" : True, "data" : rows_list}
    else:
        return {"success" : False, "error" : "No data."}

@route('/data/attention', method='POST')
def post_proximity():
    val = request.POST.get('value', -1)

    if val != -1:
        # put in db
        db = sqlite3.connect('./dress.db')
        c = db.cursor()
        c.execute("INSERT INTO attention (value) VALUES (?)", (val,))
        db.commit()
        row_id = c.lastrowid

        c.close()

        return {"success" : True, "id" : row_id}
    else:
        # error
        return {"success" : False, "error" : "No data supplied"}

@route('/data/attention/<item>')
def attention_data(item):
    db = sqlite3.connect('./dress.db')
    c = db.cursor()
    c.execute("SELECT * FROM attention WHERE id > ?", (item,))
    rows = c.fetchall()
    rows_list = []

    c.close()

    if rows:
        for row in rows:
            t = (row[0], row[1])
            rows_list.append(t)
        return {"success" : True, "data" : rows_list}
    else:
        return {"success" : False, "error" : "No data."}

@route('/data/heartrate', method='POST')
def post_proximity():
    val = request.POST.get('value', -1)

    if val != -1:
        # put in db
        db = sqlite3.connect('./dress.db')
        c = db.cursor()
        c.execute("INSERT INTO heartrate (value) VALUES (?)", (val,))
        db.commit()
        row_id = c.lastrowid

        c.close()

        return {"success" : True, "id" : row_id}
    else:
        # error
        return {"success" : False, "error" : "No data supplied"}

@route('/data/heartrate/<item>')
def heartrate_data(item):
    db = sqlite3.connect('./dress.db')
    c = db.cursor()
    c.execute("SELECT * FROM heartrate WHERE id > ?", (item,))
    rows = c.fetchall()
    rows_list = []

    c.close()

    if rows:
        for row in rows:
            t = (row[0], row[1])
            rows_list.append(t)
        return {"success" : True, "data" : rows_list}
    else:
        return {"success" : False, "error" : "No data."}

@route('/data/image', method='POST')
def image_upload():
    image = request.files.get('image')
    name, ext = os.path.splitext(image.filename)
    if ext not in ('.png', '.jpg', '.jpeg'):
        return {"success" : False, "error" : "Incorrect file type."}

    path = "images/"
    if not os.path.exists(path):
        os.makedirs(path)

    image.save(path)

    db = sqlite3.connect('./dress.db')
    c = db.cursor()
    c.execute("INSERT INTO images (url) VALUES (?)", (path+image.filename,))
    db.commit()
    row_id = c.lastrowid
    c.close()

    return {"success" : True, "id" : row_id}

@route('/data/image/<item>')
def image_data(item):
    db = sqlite3.connect('./dress.db')
    c = db.cursor()
    c.execute("SELECT * FROM images WHERE id > ?", (item,))
    rows = c.fetchall()
    rows_list = []

    c.close()

    if rows:
        for row in rows:
            t = (row[0], row[1])
            rows_list.append(t)
        return {"success" : True, "data" : rows_list}
    else:
        return {"success" : False, "error" : "No data."}

@route('/data/video')
def video_data():
    return {"success" : False, "error" : "Not implemented."}

@route('/static/:path#.+#', name='static')
def static(path):
    return static_file(path, root='static')

@route('/images/:path#.+#', name='images')
def images(path):
    return static_file(path, root='images')

run(host='192.168.42.1', port=80)