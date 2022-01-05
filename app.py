from flask import Flask, g, request, jsonify
from database import get_db
from functools import wraps

app = Flask(__name__)

# api authentication credentials
api_username = "admin"
api_password = "password"

# authentication verification decorator
def protected(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == api_username and auth.password == api_password:
            return f(*args, **kwargs)
        return jsonify({"message": "Authentication failed"}), 403

    return decorated


# close the connection once the route is visited
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()


# based on the RESTFUL API -> Building multiple requests to the same endpoints

# GET method for getting all memebers
@app.route("/member", methods=["GET"])
@protected
def get_members():

    db = get_db()
    members_cur = db.execute("select id, name, email, level from members")
    members_db = members_cur.fetchall()

    members = []
    for member_db in members_db:
        member = {
            "id": member_db["id"],
            "name": member_db["name"],
            "email": member_db["email"],
            "level": member_db["level"],
        }

        members.append(member)

    return jsonify({"members": members})


# GET method for getting one member by ID
@app.route("/member/<int:member_id>", methods=["GET"])
@protected
def get_member(member_id):

    db = get_db()
    member_cur = db.execute(
        "select id, name, email, level from members where id=?", [member_id]
    )
    member_db = member_cur.fetchone()

    return jsonify(
        {
            "member": {
                "id": member_db["id"],
                "name": member_db["name"],
                "email": member_db["email"],
                "level": member_db["level"],
            }
        }
    )


# POST method for adding one member
@app.route("/member", methods=["POST"])
@protected
def add_member():
    # getting member data from json sent in post request
    new_member = request.get_json()

    member_name = new_member["name"]
    member_email = new_member["email"]
    member_level = new_member["level"]

    db = get_db()
    db.execute(
        "insert into members (name, email, level) values ( ?, ?, ?)",
        [member_name, member_email, member_level],
    )
    db.commit()

    member_cur = db.execute(
        "select id, name, email, level from members where name=?", [member_name]
    )
    member_db = member_cur.fetchone()

    return jsonify(
        {
            "member": {
                "id": member_db["id"],
                "name": member_db["name"],
                "email": member_db["email"],
                "level": member_db["level"],
            }
        }
    )


# PUT and PATCH method for editing one member by ID
@app.route("/member/<int:member_id>", methods=["PUT", "PATCH"])
@protected
def edit_member(member_id):

    # getting member data from json sent in post request
    new_member = request.get_json()

    member_name = new_member["name"]
    member_email = new_member["email"]
    member_level = new_member["level"]

    # updating the member
    db = get_db()
    db.execute(
        "update members set name=?, email=?, level=? where id=?",
        [member_name, member_email, member_level, member_id],
    )
    db.commit()

    # returning the updated member from database
    member_cur = db.execute(
        "select id, name, email, level from members where id=?", [member_id]
    )
    member_db = member_cur.fetchone()

    return jsonify(
        {
            "member": {
                "id": member_db["id"],
                "name": member_db["name"],
                "email": member_db["email"],
                "level": member_db["level"],
            }
        }
    )


# DELETE method for deleting one member by ID
@app.route("/member/<int:member_id>", methods=["DELETE"])
@protected
def delete_member(member_id):

    # deleting the member
    db = get_db()
    db.execute(
        "delete from members where id=?",
        [member_id],
    )
    db.commit()

    return jsonify({"message": "a member has been deleted"})


if __name__ == "__main__":
    app.run(debug=True)
