from flask import Flask
from flask import render_template
from flask import request
from flask import url_for
from flask import redirect
import pickle



app = Flask(__name__)


@app.route("/")
def index():
    return render_template("top.html")


@app.route("/search",methods=["POST"])
def html():
    search = request.form["search"]
    result = []
    gomi = List.Gomi_list()
    
    for i in gomi:
        for f in i:
            if search in f[0]:
                if type(f) != str:
                    result.append(f)

    print(result)
        
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
        with open("linklist.txt", "rb") as f:
            gomi = pickle.load(f)
        return gomi



app.run()



