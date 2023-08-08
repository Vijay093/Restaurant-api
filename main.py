import random
import os
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurant.db'
db = SQLAlchemy()
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # # Method 1.
        # dictionary = {}
        # # Loop through each column in the data record
        # for column in self.__table__.columns:
        #     # Create a new dictionary entry;
        #     # where the key is the name of the column
        #     # and the value is the value of the column
        #     dictionary[column.name] = getattr(self, column.name)
        # return dictionary

        # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")
    

# HTTP GET - Read Record
@app.route("/random", methods=["GET"])
def get():
    result = db.session.execute(db.select(Cafe))
    result = result.scalars().all()
    random_cafe = random.choice(result)
    return jsonify(
        id=random_cafe.id,
        name=random_cafe.name,
        map_url=random_cafe.map_url,
        img_url=random_cafe.img_url,
        location=random_cafe.location,
        seats=random_cafe.seats,
        has_toilet=random_cafe.has_toilet,
        has_wifi=random_cafe.has_wifi,
        has_sockets=random_cafe.has_sockets,
        can_take_calls=random_cafe.can_take_calls,
        coffee_price=random_cafe.coffee_price
    )


@app.route("/all", methods=["GET"])
def all():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])


@app.route("/search")
def search():
    query_location = request.args.get('loc')
    result = db.session.execute(db.select(Cafe).where(Cafe.location == query_location))
    all_cafes = result.scalars().all()
    if all_cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404


# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def post_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


# HTTP PUT/PATCH - Update Record
@app.route("/update_price/<int:id>", methods=["PATCH"])
def patch_new_price(id):
    if db.get_or_404(Cafe, id):
        to_update = db.get_or_404(Cafe, id)
        new_price = request.form.get('new_price')
        to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully added the new cafe."})
    else:
        return jsonify(response={"failure": "Sorry a Cafe with that id was not found in database."}), 404


# HTTP DELETE - Delete Record
@app.route("/delete/<int:id>", methods=["DELETE"])
def delete_cafe(id):
    api_key = request.args.get("api-key")
    if api_key == os.environ.get('API_KEY'):
        if db.get_or_404(Cafe, id):
            to_delete = db.get_or_404(Cafe, id)
            db.session.delete(to_delete)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe from database."})
        else:
            return jsonify(response={"failure": "Sorry a Cafe with that id was not found in database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


if __name__ == '__main__':
    app.run(debug=True)
