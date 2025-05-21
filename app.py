from flask import Flask, render_template, request, jsonify
from databaseLoader import load_file_by_file, track_database, get_database_records

app = Flask(__name__)


# Route to render the form
@app.route("/")
def index():
    data = get_database_records()
    print(data)
    if data is not None:
        return render_template("index.html", response=data)
    else:
        return render_template("index.html")


# Route to handle the AJAX request
@app.route("/submit", methods=["POST"])
def submit():
    # Get data from the AJAX request
    data = request.get_json()
    dbName = data.get("name")
    folderPath = data.get("folderpath")

    try:

        load_file_by_file(dbName, folderPath)
        track_database(dbName, folderPath)
        database_records = get_database_records()
        data = {
            "status": "success",
            "message": f"Database Name - {dbName}, Folder Path  - {folderPath}",
            "response_data": {"database": dbName, "path": folderPath},
        }

        return jsonify(data)
    except:
        data = {
            "status": "fail",
            "message": f"Database Name - {dbName}, Folder Path  - {folderPath}",
        }

    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
