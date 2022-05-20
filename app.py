import os
from flask import Flask, flash, request, redirect, render_template, url_for
from pymongo import MongoClient
from random import choice
from string import ascii_uppercase
from pprint import pprint


UPLOAD_FOLDER = "./static/"
ALLOWED_EXTENSIONS = set(["txt", "pdf", "png", "jpg", "jpeg", "gif"])

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# 27017
client = MongoClient("localhost", 27017)
db = client.pfa


@app.route("/")
def index():
    id = request.args.get("id")
    all_images=[]
    if id is None:
        print("is none")
        result = db.images.find().sort("_id", -1)
    else:
        result = db.images.find({"_id": int(id)})

    count = db.images.count_documents({})
    all = db.images.find()
    if count > 0:
        image = result[0]["chemin"]
        img_id = result[0]["_id"]
        all_images = all
    else:
        image = ""
        all = []
        img_id = 0
    return render_template(
        "./index.html", img=image, img_id=img_id, all_images=all_images
    )


@app.route("/upload", methods=["POST"])
def upload_file():
    # check if the post request has the file part
    if "file" not in request.files:
        flash("No file part")
        return redirect("/")
    file = request.files["file"]
    if file.filename == "":
        flash("No selected file")
        return redirect("/")
    image_name = random() + file.filename
    chemin = os.path.join(app.config["UPLOAD_FOLDER"], image_name)
    file.save(chemin)
    save_to_db(image_name)
    return redirect(url_for("index"))


@app.route("/delete", methods=["GET"])
def delete():
    id = request.args.get("id")
    db.images.delete_one({"_id": int(id)})
    return redirect(url_for("index"))


@app.route("/select", methods=["POST"])
def select():
    id = request.form.get("id")
    x = request.form.get("x")
    y = request.form.get("y")
    h = request.form.get("h")
    w = request.form.get("w")
    db.images.update_one(
        {"_id": int(id)}, {"$set": {"x": int(x), "y": int(y), "h": int(h), "w": int(w)}}
    )
    return redirect(url_for("index"))


def save_to_db(path):
    last_one =  db.images.find().sort("_id", -1)
    db.images.insert_one(
        {
            
            "_id": int(last_one[0]["_id"]) + 1,
            "chemin": path,
            "x": 0,
            "y": 0,
            #longeur
            "h": 0,
            #largeur
            "w": 0,
        }
    )


def random():
    return "".join(choice(ascii_uppercase) for i in range(2))
