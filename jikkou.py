from flask import Flask
from flask import render_template
from flask import request
from flask import url_for
from flask import redirect
import gomi_copy


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("top.html")


@app.route("/search",methods=["POST"])
def html():
    search = request.form["search"]
    result = {}
    gomi = List.Gomi_list()
    
    for i in gomi.keys():
        
        if search in i:
            result[i] = gomi[i]
        
    return render_template("top.html", result=result,search=search)

@app.route("/camer")
def camer():
    return render_template("camer.html")
@app.route("/a",methods=["POST"])
def a():    
    file = request.files["file"]

    
    
    return render_template("camer.html")



@app.route("/characterlist")
def characterlist():
    character = ["あ","か","が","さ","ざ","た","だ","な","は","ば","ぱ","ま","や","ら","わ"]
    return render_template("characterlist.html",characterlist=character)

@app.route("/list/<int:id>")
def list(id):
    gomi = List.Gomi_list()
    character = ["あ","か","が","さ","ざ","た","だ","な","は","ば","ぱ","ま","や","ら","わ"]
    japan = character[id-1]
    for i in gomi:
        if i[0] == japan:
            new_gomi = i
            del new_gomi[0]
    print(new_gomi)
    
    return render_template("list.html",list=new_gomi,character=japan)
@app.route("/history")
def history():
    return render_template("history.html")

@app.errorhandler(404)
def show_404_page(error):
    msg = error.description
    print("エラー内容 : ",msg)

    return render_template("errors/404.html") , 404



class List():
    def Gomi_list():
        aa = gomi_copy.Garbage()
        return aa.Oshu_garbage()
    def Japanese_list():
        japanese = {"あ":["あ","い","う","え","お"],
                    "か":["か","き","く","け","こ"],
                    }
        return japanese



app.run()



