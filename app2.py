from flask import Flask, request 
import pandas as pd 
import sqlite3
app = Flask(__name__) 

conn = sqlite3.connect("data_input/chinook.db")

@app.route('/form', methods=['GET', 'POST']) #allow both GET and POST requests
def form():
    if request.method == 'POST':  # Hanya akan tampil setelah melakukan POST (submit) form
        key1 = 'name'
        key2 = 'song'
        name = request.form.get(key1)
        song = request.form[key2]
        
        return (f'''<h1>Hello, {name}!</h1>
                   <h2>I see that you love listening to {song}! Me too! I'm not here to recommend you songs though, I'm here because I'm able to deploy API endpoints from data about songs. Isn't it cool?</h2>
                   <h2> Maybe you can find something useful and find your next favourite songs out of this!</h2>
                   <h2> Have a great day ahead! </h2>
                ''')
   
    
    return '''<form method="POST">
                  Name: <input type="text" name="name"><br>
                  Favourite Song: <input type="text" name="song"><br>
                  <input type="submit" value="Submit"><br>
              </form>'''

# mendapatkan keseluruhan data dari <data_name>
@app.route('/data/get/<data_name>', methods=['GET']) 
def get_data(data_name): 
    data = pd.read_csv('data/' + str(data_name))
    return (data.to_json())
    

# mendapatkan data dengan filter nilai <value> pada kolom <column>
@app.route('/data/get/equal/<data_name>/<column>/<value>', methods=['GET']) 
def get_data_equal(data_name, column, value): 
    data = pd.read_csv('data/' + str(data_name))
    mask = data[column] == value
    data = data[mask]
    return (data.to_json())

if __name__ == '__main__':
    app.run(debug=True, port=5000)