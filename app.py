from flask import Flask, render_template, request, session
import csv
import uuid
import pandas as pd

app = Flask(__name__)
app.secret_key = 'LETS-KEEP-SOME-SECRET-HERE'

def get_status(row):
    if row['feedback_yes_count'] >= 3:
        return 'Yes'
    elif row['feedback_no_count'] >= 3:
        return 'No'
    else:
        return 'Hey'
status_changed_rows =[]
def get_rows():
    df = pd.read_csv('dataset.csv')
    feedback_cols = df.filter(regex='^feedback')
    df['feedback_yes_count'] = feedback_cols.eq('Yes').sum(axis=1)
    df['feedback_no_count'] = feedback_cols.eq('No').sum(axis=1)
    if 'status' not in df.columns:
        return df.to_dict(orient='records'),[]
    return df[df['status'] == 'Hey'].to_dict(orient='records'),df[df['status'] != 'Hey'].to_dict(orient='records')

@app.route("/", methods=["GET", "POST"])
def feedback():  # sourcery skip: assign-if-exp, switch

    try:

        global status_changed_rows
        if request.method == "GET":
            rows,status_changed_rows = get_rows()
            # session['status_changed_rows'] = status_changed_rows
            if rows:
                session["rows"] = rows
                session["row_index"] = 0
                session["uuid"] = str(uuid.uuid4())
                uuid_key = f"feedback_{session['uuid']}"
                return render_template("feedback.html", row=rows[0])
            return render_template("completed.html")

        elif request.method == "POST":
            
            feedback = request.form["feedback"]
            uuid_key = f"feedback_{session['uuid']}"
            rows = session["rows"]
            row_index = session["row_index"]
            rows[row_index][uuid_key] = feedback
            if rows[row_index][uuid_key] == 'Yes':
                rows[row_index]['feedback_yes_count'] += 1
            else:
                rows[row_index]['feedback_no_count'] += 1

            updated_df = pd.DataFrame().from_dict(rows+status_changed_rows)
            updated_df['status'] = updated_df.apply(get_status, axis=1)

            updated_df.to_csv('dataset.csv', index=False)

            session["row_index"] += 1
            if session["row_index"] < len(rows):
                return render_template("feedback.html", row=rows[session["row_index"]])
            else:
                return "Thank you for your feedback!"
    except:
        return "Some error occured :( .,refresh or try again later"
if __name__ == "__main__":
    app.run(debug=True, port=5001, host='0.0.0.0')

