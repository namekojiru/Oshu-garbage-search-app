from flask import Flask,render_template,make_response,request,redirect,url_for,flash,g
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
import json
import calendar
import re
import jpholiday

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
def get_day_of_nth_dow(year, month, nth, dow):
    '''
    指定された年月の第nth番目のdow曜日 (月=0 - 日=6) が何日であるかを計算します。
    dow: Monday(0) - Sunday(6)
    '''
    if nth < 1 or dow < 0 or dow > 6:
        return None

    first_dow, n = calendar.monthrange(year, month) # first_dow は月の1日の曜日 (月=0 - 日=6)
    
    # 計算式を修正: (dow - first_dow) が負の値になる場合を考慮し、常に0-6の範囲に収める
    # 例: first_dow=2(水), dow=0(月) の場合、(0 - 2 + 7) % 7 = 5 となり、水曜日から月曜日までのオフセットが正しく計算される
    day_offset_from_first_day_of_week = (dow - first_dow + 7) % 7
    day = 7 * (nth - 1) + day_offset_from_first_day_of_week + 1

    return day if day <= n else None

# get_nth_week と get_nth_dow はこのプログラムの主要なロジックには直接関与しないため、そのまま保持
def get_nth_week(day):
    return (day - 1) // 7 + 1

def get_nth_dow(year, month, day):
    return get_nth_week(day), calendar.weekday(year, month, day)

def collection_date_calendar(year,months,burns,not_burns):
    calendars = []
    kaisyu_youbi = burns # 強調表示する曜日
    kaisyu_n_date = not_burns # 強調表示する特定の日

    # 週の始まりを日曜日(6)に設定（calendar.monthcalendarに影響）
    calendar.setfirstweekday(6) # 日曜日が週の最初の曜日になる (index 0)

    # calendar.getfirstweekday() は存在しないため、直接設定値を使用
    # 週の最初の曜日は 6 (日曜日) と設定されている
    WEEK_START_DOW = 6

    # kaisyu_youbi を現在の calendar.setfirstweekday() の設定に合わせたインデックスに変換
    # 例: 日曜日始まりの場合 (WEEK_START_DOW = 6)
    # オリジナル曜日 (月=0) -> (0 - 6 + 7) % 7 = 1 (インデックス1)
    # オリジナル曜日 (火=1) -> (1 - 6 + 7) % 7 = 2 (インデックス2)
    # オリジナル曜日 (金=4) -> (4 - 6 + 7) % 7 = 5 (インデックス5)
    # オリジナル曜日 (日=6) -> (6 - 6 + 7) % 7 = 0 (インデックス0)
    converted_kaisyu_youbi_indices = []
    for original_dow in kaisyu_youbi:
        converted_index = (original_dow - WEEK_START_DOW + 7) % 7
        converted_kaisyu_youbi_indices.append(converted_index)

    # kaisyu_n_date の dow も同様に変換
    original_kaisyu_n_dow = kaisyu_n_date[1]
    # converted_kaisyu_n_dow_index = (original_kaisyu_n_dow - WEEK_START_DOW + 7) % 7
    # converted_kaisyu_n_date = (kaisyu_n_date[0], converted_kaisyu_n_dow_index)
    # -> get_day_of_nth_dow は内部で月曜始まりを仮定しているので、この変換は不要。
    #    kaisyu_n_date[1] はそのまま get_day_of_nth_dow に渡せばOK。

    for month in months:
        This_month = (year,month)

        # get_day_of_nth_dow に渡す dow は元の定義 (月=0) のままで良い。
        # 関数内部で calendar.monthrange の first_dow (月=0) との整合性を取っているため。
        kaisyu_n = get_day_of_nth_dow(This_month[0],This_month[1],kaisyu_n_date[0],kaisyu_n_date[1])

        kaisyu_y = []
        # kaisyu_y の計算ロジックを修正: calendar.monthcalendar を活用
        # converted_kaisyu_youbi_indices を使用し、設定された週の始まりに合わせた正しい曜日インデックスで日付を取得
        for converted_index_dow in converted_kaisyu_youbi_indices:
            for week in calendar.monthcalendar(This_month[0], This_month[1]):
                # week は [日, 月, 火, 水, 木, 金, 土] の順に日付が格納されている (setfirstweekday(6) のため)
                day_in_week = week[converted_index_dow]
                if day_in_week != 0: # 月に属する日付であれば
                    kaisyu_y.append(day_in_week)
        kaisyu_y = sorted(list(set(kaisyu_y))) # 重複を削除し、ソート

        mondays = []
        # kaisyu_y の計算ロジックを修正: calendar.monthcalendar を活用
        # converted_kaisyu_youbi_indices を使用し、設定された週の始まりに合わせた正しい曜日インデックスで日付を取得

        for week in calendar.monthcalendar(This_month[0], This_month[1]):
            # week は [日, 月, 火, 水, 木, 金, 土] の順に日付が格納されている (setfirstweekday(6) のため)
            day_in_week = week[1]
            if day_in_week != 0: # 月に属する日付であれば
                mondays.append(day_in_week)
        mondays = sorted(list(set(mondays))) # 重複を削除し、ソート

        calendar_list = calendar.monthcalendar(This_month[0],This_month[1])

        the_calendar_list = []
        for i_week in calendar_list: # i を i_week に変更 (変数の衝突を避けるため)
            week_list = []
            for f_day in i_week: # f を f_day に変更 (変数の衝突を避けるため)
                if f_day in mondays:
                    if f_day == kaisyu_n:
                        week_list.append([f_day,"n"]) # 特定のN番目の日
                    elif f_day in kaisyu_y: # 複数条件があるため elif で連結
                        week_list.append([f_day,"y"]) # 指定曜日の日
                    else:
                        week_list.append(f_day) # 通常の日付
                else:
                    if not f_day == 0:
                        if jpholiday.is_holiday(datetime.date(This_month[0], This_month[1], f_day)):
                            if f_day == kaisyu_n:
                                kaisyu_n += 7
                            week_list.append(f_day) # 通常の日付
                            print(month,f_day)
                        else:
                            if f_day == kaisyu_n:
                                week_list.append([f_day,"n"]) # 特定のN番目の日
                            elif f_day in kaisyu_y: # 複数条件があるため elif で連結
                                week_list.append([f_day,"y"]) # 指定曜日の日
                            else:
                                week_list.append(f_day) # 通常の日付
                    else:
                        week_list.append(0)


            the_calendar_list.append(week_list)

        calendars.append(the_calendar_list)
    return calendars,months
    
@app.route("/",methods=["GET","POST"])
def index():
    if request.method == "POST":
        search = request.form.get("search")
        result = []
        if search != "":

            gomi = List.Gomi_list(request.args.get("lang"))
            
            for i in gomi:
                if search in i[0]:
                    result.append(i)
            global response

            max_age = 10
            expires = int(datetime.datetime.now().timestamp()) + max_age * 86400
            response = make_response(render_template("top.html", result=result, search=search,lang=lang()))

            history = request.cookies.get('history')
            if history is not None:
                history = json.loads(history)
                history.append([search,datetime.date.today()])
            else:
                history = [(search,datetime.date.today())]
            response.set_cookie("history", value=json.dumps(history,default=str), expires=expires)

            return response
    return render_template("top.html", result="", search="",lang=lang())


@app.route("/camer",methods=["POST","GET"])
def camer():
    search_gomi = ["缶","ティッシュペーパーの箱","ビン","鉛筆","ペットボトル","本","ペン","靴","カッター","マウス"]
    search_gomi_en = ["Can", "tissue box", "bottle", "pencil", "plastic bottle", "book", "pen", "shoes", "cutter", "mouse"]
    search_gomi_ko = ["캔", "티슈 페이퍼 상자", "병", "연필", "페트병", "책", "펜", "구두", "커터", "마우스"]
    search_gomi_zh = ["罐头","一盒薄纸","瓶子","铅笔","塑料瓶","书","笔","鞋","刀具","鼠标"]
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
        # Load the image into the array
        data[0] = convert_to_rgb(normalized_image_array)

        prediction = model.predict(data)

        prediction = [round(i*100) for i in prediction[0]]

        search = dict(zip(search_gomi, prediction))
        search = dict(sorted({f:i for f,i in search.items() if i > 30}.items()))
        result = {}
        gomi = List.Gomi_list("ja")
        for i in search.keys():

            for f in gomi:

                if i in f[0]:

                    if request.args.get("lang") == "en":
                        gomi_index = f[4]
                        gomi_lang = List.Gomi_list("en")
                        search_lang = dict(zip(search_gomi_en, prediction))
                        search_lang = dict(sorted({k:v for k,v in search_lang.items() if v > 30}.items()))
                        for g in gomi_lang:
                            if gomi_index == g[4]:
                                result[g] = search_gomi_en[search_gomi.index(i)]
                    elif request.args.get("lang") == "ko":
                        gomi_index = f[4]
                        gomi_lang = List.Gomi_list("ko")
                        search_lang = dict(zip(search_gomi_ko, prediction))
                        search_lang = dict(sorted({k:v for k,v in search_lang.items() if v > 30}.items()))
                        for g in gomi_lang:
                            if gomi_index == g[4]:
                                result[g] = search_gomi_ko[search_gomi.index(i)]
                    elif request.args.get("lang") == "zh":
                        gomi_index = f[4]
                        gomi_lang = List.Gomi_list("zh")
                        search_lang = dict(zip(search_gomi_zh, prediction))
                        search_lang = dict(sorted({k:v for k,v in search_lang.items() if v > 30}.items()))
                        for g in gomi_lang:
                            if gomi_index == g[4]:
                                result[g] = search_gomi_zh[search_gomi.index(i)]
                    else:
                        result[f] = i
                        search_lang = search
        
        search_lang = dict(sorted(search_lang.items(), key = lambda fruit : fruit[1], reverse=True))

                        
        max_age = 10
        expires = int(datetime.datetime.now().timestamp()) + max_age * 86400
        response = make_response(render_template("camer.html", filename=filename, search=search_lang, result=result, lang=lang()))

        history = request.cookies.get('history')
        if history is not None:
            history = json.loads(history)
            for i in search.keys():
                history.append([i,datetime.date.today()])
        else:
            history = [(i,datetime.date.today())]
        response.set_cookie("history", value=json.dumps(history,default=str), expires=expires)
        return response
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

@app.route("/list/<title>")
def gomilist(title):
    
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
@app.route("/history",methods=["GET","POST"])
def history():
    history = request.cookies.get('history')
    if history is not None:
        history = json.loads(history)
        if request.method == "GET":
            return render_template("history.html",history=history,lang=lang())
        else:
            if int(request.form.get("del_index")) >= 0:
                max_age = 10
                expires = int(datetime.datetime.now().timestamp()) + max_age * 86400
                del history[(len(history)-1)-int(request.form.get("del_index"))]
                response = make_response(render_template("history.html",history=history,lang=lang()))
                response.set_cookie("history", value=json.dumps(history,default=str), expires=expires)

                return response
            else:
                max_age = 10
                expires = int(datetime.datetime.now().timestamp()) + max_age * 86400
                history.clear()
                response = make_response(render_template("history.html",history=history,lang=lang()))
                response.set_cookie("history", value=json.dumps(history,default=str), expires=expires)

                return response

    return render_template("history.html",history=history,lang=lang())

@app.route("/calendar",methods=["GET","POST"])
def gomi_calendar():
    a_a,a_b=collection_date_calendar(2025,range(1,13),[1,4],[2,2])
    if request.method == "GET":
        return render_template("calendar.html",calendar=[],monthese=[])

    else:
        return render_template("calendar.html",calendar=a_a,monthes=a_b)

@app.template_filter("type")
def flask_type(argument):
    return re.findall("'.*'",str(type(argument)))[0]

@app.errorhandler(404)
def show_404_page(error):
    msg = error.description
    print("エラー内容 : ",msg)

    return render_template("errors/404.html") , 404
class List():
    def Gomi_list(lang):
        gomi = []

        if lang == "en":
            for count,i in enumerate(Oshu_gomi_en.select()):
                a = (i.gomi_en,i.category_en,i.material_en,i.title_en,count)
                gomi.append(a)
        elif lang == "zh":
            for count,i in enumerate(Oshu_gomi_zh.select()):
                a = (i.gomi_zh,i.category_zh,i.material_zh,i.title_zh,count)
                gomi.append(a)
        elif lang == "ko":
            for count,i in enumerate(Oshu_gomi_ko.select()):
                a = (i.gomi_ko,i.category_ko,i.material_ko,i.title_ko,count)
                gomi.append(a)
        else:
            for count,i in enumerate(Oshu_gomi.select()):
                a = (i.gomi,i.category,i.material,i.title,count)
                gomi.append(a)
        
        return gomi

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



