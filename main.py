from flask import Flask, redirect, url_for, render_template, request
from ucenik import *
import sqlite3
from elo import rate_1vs1


def insert_ucenik(ucenik):
    with conn:
        c.execute("INSERT INTO ucenici VALUES (?, ?, ?)", (ucenik.name, ucenik.razred, ucenik.elo))


def get_elo(name):
    c.execute("SELECT elo FROM ucenici WHERE name = :name", {'name': name})
    elo = c.fetchone()[0]
    return elo


def get_ucenik():
    c.execute("SELECT * FROM ucenici")
    return c.fetchall()


def remove_ucenik(namedel):
    with conn:
        c.execute("DELETE from ucenici WHERE name = :name",
                  {'name': namedel})


def update_elo(name, elo):
    with conn:
        c.execute("""UPDATE ucenici SET elo = :elo
                        WHERE name = :name """, {'name': name, 'elo': elo})

conn = sqlite3.connect('ucenici.db', check_same_thread=False)
c = conn.cursor()
app = Flask(__name__)

lista = []

@app.route("/index.html")
def index():
    return render_template("index.html")


@app.route("/addplayer.html", methods=["POST", "GET"])
def addplayer():
    if request.method == "POST":
        conn = sqlite3.connect('ucenici.db')
        c = conn.cursor()
        name = request.form["nm"]
        razred = request.form["raz"]
        ucenik = Ucenik(name, razred)
        insert_ucenik(ucenik)
        return redirect(url_for("elo"))
    else:
        return render_template("addplayer.html")


@app.route("/elo.html")
def elo():
    lista = get_ucenik()
    return render_template("elo.html", ucenik = lista)


@app.route("/delete.html", methods=["POST", "GET"])
def delete():
    if request.method == "POST":
        conn = sqlite3.connect('ucenici.db')
        c = conn.cursor()
        name = request.form["nmdel"]
        remove_ucenik(name)
        lista = get_ucenik()
        return render_template("delete.html", ucenik = lista)
    else:
        lista = get_ucenik()
        return render_template("delete.html", ucenik = lista)


@app.route("/match.html", methods=["POST", "GET"])
def match():
    if request.method == "POST":
        conn = sqlite3.connect('ucenici.db')
        c = conn.cursor()
        lista = get_ucenik()
        win = request.form["nmm1"]
        lose = request.form["nmm2"]
        elo1 = int(get_elo(win))
        elo2 = int(get_elo(lose))
        if request.form["draw"]:
            new_elo1, new_elo2 = rate_1vs1(elo1, elo2, True)
        else:
            new_elo1, new_elo2 = rate_1vs1(elo1, elo2)
        update_elo(win, int(new_elo1))
        update_elo(lose, int(new_elo2))
        lista = get_ucenik()
        return render_template("match.html", ucenik = lista)
    else:
        lista = get_ucenik()
        return render_template("match.html", ucenik = lista)



if __name__ == "__main__":
    app.run(debug=True)

conn.close()
