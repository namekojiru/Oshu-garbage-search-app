from flask import Flask,render_template,request,redirect,url_for,flash
from PIL import Image, ImageOps
from peewee import *
import datetime
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory
from keras.models import load_model
from PIL import Image
import numpy as np

UPLOAD_FOLDER = './static/uploads'

ALLOWED_EXTENSIONS = set(['png', 'jpg'])

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

    search = request.args.get("search","")
    result = []
    if search != "":


        dt_now = datetime.datetime.now()
        a = Rireki(gomi = search, time = dt_now)
        a.save()

        gomi = List.Gomi_list()
        
        for i in gomi:
            if search in i[0]:
                result.append(i)

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
            model = load_model("./keras_model.h5", compile=False)

            # Load the labels
            class_names = ["本","鉛筆","缶","ペットボトル","ビン"]

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

            prediction = model.predict(data)

            prediction = [round(i*100) for i in prediction[0]]

            search = dict(zip(class_names, prediction))
            search = dict(sorted({f:i for f,i in search.items() if i > 30}.items()))
            print(search)
            result = {}

            gomi = List.Gomi_list()
            for i in search.keys():
                for f in gomi:
                    if i in f[0]:
                        result[f] = i
            print(result)
            
            return render_template("camer.html",filename=filename,search=search,result=result)
    else:
        return render_template("camer.html",filename="",search="",result=[])

@app.route("/characterlist")
def characterlist():

    gomi = List.Gomi_list()
    gomi_title = []
    for i in gomi:
        gomi_title.append(i[3])
    title_list = []
    [title_list.append(x) for x in gomi_title if x not in title_list]

    return render_template("characterlist.html",gomi=title_list)

@app.route("/list")
def list():
    title = request.args.get("title","")
    result = []
    gomi=List.Gomi_list()
    for i in gomi:
        if title == i[3]:
            result.append(i)
                
    return render_template("list.html",result=result,title=title)
@app.route("/history")
def history():
    return render_template("history.html",Rireki=Rireki)

@app.route("/delete/<int:id>",methods=["POST"])
def delete_history(id):
    rireki=Rireki.get(Rireki.id == id)
    rireki.delete_instance()
    return redirect(url_for("history"))

@app.route("/all_delete",methods=["POST"])
def all_delete_history():
    Rireki.delete().execute()
    return redirect(url_for("history"))

@app.errorhandler(404)
def show_404_page(error):
    msg = error.description
    print("エラー内容 : ",msg)

    return render_template("errors/404.html") , 404

class List():
    def Gomi_list():
        gomi = []

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

oushu_db = SqliteDatabase('gomi.db')

class Oshu_gomi(Model):
    gomi = CharField()
    category = CharField()
    material = CharField(null = True)
    title = CharField()
    class Meta:
        database = oushu_db

app.run(host="0.0.0.0",debug=True)



