from flask import Flask,render_template,request,redirect,url_for,flash,g
from PIL import Image, ImageOps
from peewee import *
import datetime
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory
from keras.models import load_model
from PIL import Image
import numpy as np
from flask import render_template
from flask import current_app as app



UPLOAD_FOLDER = './app/static/uploads'

ALLOWED_EXTENSIONS = set(['png', 'jpg'])

app.secret_key = 'secret_key'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allwed_file(filename):
    # .があるかどうかのチェックと、拡張子の確認
    # OKなら１、だめなら0
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_rgb(image):
    if image.shape == (224,224,4):
        image = image[:,:,:3]
    return image    

def lang():
    l = request.args.get("lang")
    if l == None:
        return "?lang=ja"
    else:
        return "?lang="+l

    
@app.route("/")
def index():
    search = request.args.get("search","")
    result = []
    if search != "":
        
        dt_now = datetime.datetime.now()
        a = Rireki(gomi = search, time = dt_now)
        a.save()

        gomi = List.Gomi_list(request.args.get("lang"))
        
        for i in gomi:
            if search in i[0]:
                result.append(i)
    
    return render_template("top.html", result=result, search=search,lang=lang())


@app.route("/camer",methods=["POST","GET"])
def camer():
    gomi = ["缶","ティッシュペーパーの箱","ビン","鉛筆","ペットボトル","本","ペン","靴","カッター","マウス"]
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('ファイルがありません')
            return redirect(request.url)
        # データの取り出し
        file = request.files['file']
        # ファイル名がなかった時の処理
        if file.filename == '':
            flash('ファイルがありません')
            return redirect(request.url)
        # ファイルのチェック
        if file and allwed_file(file.filename):
            # 危険な文字を削除（サニタイズ処理）
            filename = secure_filename(file.filename)
            # ファイルの保存
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # アップロード後のページに転送
            img = Image.open(f"./app/static/uploads/{filename}")

            np.set_printoptions(suppress=True)

            # Load the model
            model = load_model("./app/keras_model.h5", compile=False)

            # Create the array of the right shape to feed into the keras model
            # The 'length' or number of images you can put into the array is
            # determined by the first position in the shape tuple, in this case 1
            data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

            # Replace this with the path to your image
            image = Image.open(f"./app/static/uploads/{filename}")

            # resizing the image to be at least 224x224 and then cropping from the center
            size = (224, 224)
            image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)

            # turn the image into a numpy array
            image_array = np.asarray(image)

            # Normalize the image
            normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
            aa = convert_to_rgb(normalized_image_array)
            # Load the image into the array
            data[0] = aa

            prediction = model.predict(data)

            prediction = [round(i*100) for i in prediction[0]]

            search = dict(zip(gomi, prediction))
            search = dict(sorted({f:i for f,i in search.items() if i > 30}.items()))
            print(search)
            result = {}

            gomi = List.Gomi_list(request.args.get("lang"))
            for i in search.keys():
                dt_now = datetime.datetime.now()
                a = Rireki(gomi = i, time = dt_now)
                a.save()
                for f in gomi:
                    if i in f[0]:
                        result[f] = i
            print(result)
            
            return render_template("camer.html",filename=filename,search=search,result=result,lang=lang())
    else:
        return render_template("camer.html",filename="",search="",result=[],lang=lang())

@app.route("/characterlist")
def characterlist():

    gomi = List.Gomi_list(request.args.get("lang"))
    if str(request.args.get("lang")) in ["en","zh","ko"]:
        title_list = [ "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
    else:
        gomi_title = []
        for i in gomi:
            gomi_title.append(i[3])
        title_list = []
        [title_list.append(x) for x in gomi_title if x not in title_list]

    return render_template("characterlist.html",gomi=title_list,lang=lang())

@app.route("/list")
def list():
    title = request.args.get("title","")
    result = []
    if str(request.args.get("lang")) ==  "ja":
        gomi=List.Gomi_list(request.args.get("lang"))
        for i in gomi:
            if title == i[3]:
                result.append(i)
    else:
        gomi=List.Gomi_list("en")
        gomi_index = []
        print(gomi)
        for i in gomi:
            if title == i[3]:
                gomi_index.append(gomi.index(i))
        gomi=List.Gomi_list(request.args.get("lang"))
        for i in gomi:
            if gomi.index(i) in gomi_index:
                result.append(i)

    return render_template("list.html",result=result,title=title,lang=lang())
@app.route("/history")
def history():
    return render_template("history.html",Rireki=Rireki,lang=lang())

@app.route("/delete/<int:id>",methods=["POST"])
def delete_history(id):
    rireki=Rireki.get(Rireki.id == id)
    rireki.delete_instance()
    return redirect(url_for("history"))

@app.route("/all_delete",methods=["POST"])
def all_delete_history():
    Rireki.delete().execute()
    rireki_db.create_tables([Rireki])
    return redirect(url_for("history"))

@app.errorhandler(404)
def show_404_page(error):
    msg = error.description
    print("エラー内容 : ",msg)

    return render_template("errors/404.html") , 404
class List():
    def Gomi_list(lang):
        gomi = []

        if lang == "en":
            for i in Oshu_gomi_en.select():
                a = (i.gomi_en,i.category_en,i.material_en,i.title_en)
                gomi.append(a)
        elif lang == "zh":
            for i in Oshu_gomi_zh.select():
                a = (i.gomi_zh,i.category_zh,i.material_zh,i.title_zh)
                gomi.append(a)
        elif lang == "ko":
            for i in Oshu_gomi_ko.select():
                a = (i.gomi_ko,i.category_ko,i.material_ko,i.title_ko)
                gomi.append(a)
        else:
            for i in Oshu_gomi.select():
                a = (i.gomi,i.category,i.material,i.title)
                gomi.append(a)
        
        return gomi

rireki_db = SqliteDatabase('rireki.db')

class Rireki(Model):
    gomi = CharField()
    time = DateTimeField()

    class Meta:
        database = rireki_db
rireki_db.create_tables([Rireki])

gomi_db = SqliteDatabase('gomi.db')

class Oshu_gomi(Model):
    gomi = CharField()
    category = CharField()
    material = CharField(null = True)
    title = CharField()
    class Meta:
        database = gomi_db
class Oshu_gomi_en(Model):
    gomi_en = CharField()
    category_en = CharField()
    material_en = CharField(null = True)
    title_en  = CharField()
    class Meta:
        database = gomi_db
class Oshu_gomi_zh(Model):
    gomi_zh = CharField()
    category_zh = CharField()
    material_zh = CharField(null = True)
    title_zh  = CharField()
    class Meta:
        database = gomi_db
class Oshu_gomi_ko(Model):
    gomi_ko = CharField()
    category_ko = CharField()
    material_ko = CharField(null = True)
    title_ko  = CharField()
    class Meta:
        database = gomi_db
app.run(host="0.0.0.0",debug=True)



