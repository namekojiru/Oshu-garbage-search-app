from flask import Flask,render_template,request,redirect,url_for,flash
from PIL import Image, ImageOps
import pickle
from peewee import *
import datetime
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory
from keras.models import load_model
from PIL import Image
import numpy as np

UPLOAD_FOLDER = './static/uploads'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif'])

app = Flask(__name__)
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
    


@app.route("/")
def index():
    return render_template("top.html")


@app.route("/search",methods=["POST","GET"])
def html():
    if request.method == "POST":
        search = request.form["search"]
        result = []

        dt_now = datetime.datetime.now()
        a = Rireki(gomi = search, time = dt_now)
        a.save()

        gomi = List.Gomi_list()
        
        for i in gomi:
            for f in i:
                if search in f[0]:
                    if type(f) != str:
                        result.append(f)
        return render_template("top.html", result=result, search=search)

    else:

        search = request.args.get("search","")
        result = []
        
        

        gomi = List.Gomi_list()
        
        for i in gomi:
            for f in i:
                if search in f[0]:
                    if type(f) != str:
                        result.append(f)
        return render_template("top.html", result=result, search=search)

            

@app.route("/camer",methods=["POST","GET"])
def camer():
    gomi = ["ペットボトル","缶","ビン"]
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
            img = Image.open(f"./static/uploads/{filename}")

            np.set_printoptions(suppress=True)

            # Load the model
            model = load_model("./keras_Model.h5", compile=False)

            # Load the labels
            class_names = open("./labels.txt", "r").readlines()

            # Create the array of the right shape to feed into the keras model
            # The 'length' or number of images you can put into the array is
            # determined by the first position in the shape tuple, in this case 1
            data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

            # Replace this with the path to your image
            image = Image.open(f"./static/uploads/{filename}")

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

            # Predicts the model
            prediction = model.predict(data)
            index = np.argmax(prediction)
            class_name = class_names[index]
            confidence_score = prediction[0][index]

            # Print prediction and confidence score
            search = gomi[int(class_name[2:])]

            result = []

            dt_now = datetime.datetime.now()
            a = Rireki(gomi = search, time = dt_now)
            a.save()

            gomi = List.Gomi_list()
            
            for i in gomi:
                for f in i:
                    if search in f[0]:
                        if type(f) != str:
                            result.append(f)
            
            return render_template("camer.html",filename=filename,search=search,result=result)
    else:
        return render_template("camer.html")

@app.route("/characterlist")
def characterlist():
    gomi = List.Gomi_list()
    gomi_initials = []
    for i in gomi:
        for f in i:
            if type(f) == str:
                gomi_initials.append(f)
    return render_template("characterlist.html",gomi=gomi_initials)

@app.route("/list/<int:id>")
def list(id):
    gomi = List.Gomi_list()
    gomi_initials = []
    for i in gomi:
        for f in i:
            if type(f) == str:
                gomi_initials.append(f)
    
    japan = gomi_initials[id]
    for i in gomi:
        if i[0] == japan:
            new_gomi = i
            del new_gomi[0]
                
    return render_template("list.html",list=new_gomi,character=japan)
@app.route("/history")
def history():
    return render_template("history.html",Rireki=Rireki)

@app.errorhandler(404)
def show_404_page(error):
    msg = error.description
    print("エラー内容 : ",msg)

    return render_template("errors/404.html") , 404


class List():
    def Gomi_list():
        with open("linklist.txt", "rb") as f:
            gomi = pickle.load(f)
        return gomi

rireki_db = SqliteDatabase('rirekis.db')


class Rireki(Model):
    gomi = CharField()
    time = DateTimeField()

    class Meta:
        database = rireki_db
oshu_db = SqliteDatabase("gomi.db")

class Oshu_gomi(Model):
    gomi = CharField()
    category = CharField()
    material = CharField()
    class Meta:
        database = oshu_db

app.run(host="0.0.0.0",debug=True)



