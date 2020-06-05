from flask import Flask, request 
import pandas as pd 
import sqlite3
app = Flask(__name__) 

conn = sqlite3.connect("data/chinook.db")
songs = pd.read_sql_query('''SELECT t.name as Song, g.name as Genre, a.title as Album,
ar.name as ArtistName, m.name as MediaTypes, t.unitprice as UnitPrice, t.Composer,
i.CustomerId, c.firstname|| ' ' ||c.lastname as customername, ii.Quantity,
i.InvoiceDate,i.Billingcity as City,i.billingCountry as Country, t.trackid
from tracks t
left join playlist_track on playlist_track.trackid = t.name
left join playlists p on playlist_track.playlistid = p.playlistid
left join media_types m on m.mediatypeid = t.mediatypeid
left join genres g on g.genreid = t.genreid
left join albums a on a.albumid = t.albumid
left join artists ar on ar.artistid = a.artistid
left join invoice_items ii on ii.trackid = t.trackid
left join invoices i on ii.invoiceid = i.invoiceid
left join customers c on i.customerid = c.customerid''', conn, parse_dates='InvoiceDate')

#Change data types
songs[['Genre', 'ArtistName', 'MediaTypes', 'City', 'Country', 'Album']] = songs[['Genre', 'ArtistName', 'MediaTypes', 'City', 'Country', 'Album']].astype('category')

#Fill NA
songs["Composer"].fillna('Unknown',inplace=True)
songs["Quantity"].fillna(0,inplace=True)

#Drop the remaining duplicates and NA
songs = songs.drop_duplicates()
songs = songs.dropna(how = 'any')

#Reset Index
songs = songs.reset_index(drop = True)

#Top 10 songs most bought by customers
toptensongs = pd.crosstab(index = [songs.Song, songs.ArtistName],
                  columns = 'freq',
                  values = songs.Quantity,
                  aggfunc = 'sum').sort_values('freq', ascending = False)
top10songs = toptensongs.reset_index(level=['Song', 'ArtistName']).head(10)

#Top 10 Artists
toptenartists = toptensongs.stack().to_frame().groupby(['ArtistName']).sum().sort_values(0, ascending = False).head(10)
top10artists = toptenartists.reset_index(level='ArtistName')

#Top 10 Genres
toptengenres = pd.crosstab(index = songs["Genre"],
           columns = 'frequency',
           values = songs.Quantity,
           aggfunc = 'sum').sort_values('frequency', ascending = False).head(10)
top10genres = toptengenres.reset_index(level='Genre')

#Extract year from invoice date
songs['Year'] = songs.InvoiceDate.dt.year

#Catalogue
catalogue = songs.loc[:, ('Song', 'Genre', 'Album', 'ArtistName', 'MediaTypes', 'UnitPrice')]

songs.Quantity = songs.Quantity.astype('int')
songs.CustomerId = songs.CustomerId.astype('int')

songs.Year = songs.Year.apply(str)
songs.UnitPrice = songs.UnitPrice.apply(str)
songs.Quantity = songs.Quantity.apply(str)
songs.CustomerId = songs.CustomerId.apply(str)
songs.TrackId = songs.TrackId.apply(str)

sales = songs.copy()


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

@app.route("/docs")
def documentation():
    #<ol> is ordered list
    #<li> is list
    #<ul> is unordered list
    return '''
    <h1> Documentation of Endpoints </h1>
    <h2> Static Endpoints: </h2>
    <ol>
        <li>
            <p> Base endpoint that is interactive and let's the user compute their name and favourite song: </p>
            <p> /form, method = POST </p>
        </li>
        <li>
            <p> Documentation about the use of API: </p>
            <p> /docs, method = GET </p>
        </li>
        <li>
            <p> To show the whole list of songs: </p>
            <p> /data/get/catalogue, method = GET </p>
        </li>
        <li>
            <p> To show top 10 songs from the number of sales: </p>
            <p> /data/get/top10songs, method = GET </p>
        </li>
        <li>
            <p> To show top 10 artists from the number of sales: </p>
            <p> /data/get/top10artists, method = GET </p>
        </li>
        <li>
            <p> To show top 10 genres from the number of sales: </p>
            <p> /data/get/top10genres, method = GET </p>
        </li>
    </ol>
    <h2> Dynamic Endpoints: </h2>
    <ol>
            <p> To show the whole data on sales </p>
            <p> /data/get/sales , method = GET </p>
            <p> To filter based on your desired conditions: </p>
            <p> /data/get/equal/data_name]/column]/[value], where [data_name] is sales. </p>
            <p> For example: </p>
            <ol style="list-style-type:disc;">
                <li> <p> When you want to filter based on the country where the purchase of the songs are made, you can enter: </p>
                <p> /data/get/equal/sales/Country/Germany </p> </li>
                <li> When you want to filter based on the year of the purchase of the songs, you can enter: </p>
                <p> /data/get/equal/sales/Year/2009 </p> </li>
                <li> When you want to filter based on the artist, you can enter: </p>
                <p> /data/get/equal/sales/ArtistName/U2 </p> </li>
                <li> When you want to filter based on the genre, you can enter: </p>
                <p> /data/get/equal/sales/Genre/Classical </p> </li> </ol>
            And so on...
    </ol>
    '''

@app.route('/data/get/catalogue', methods=['GET']) 
def get_catalogue():
    return (catalogue.to_json())

@app.route('/data/get/top10songs', methods=['GET']) 
def get_top10songs(): 
    return (top10songs.to_json())

@app.route('/data/get/top10artists', methods=['GET']) 
def get_top10artists(): 
    return (top10artists.to_json())

@app.route('/data/get/top10genres', methods=['GET']) 
def get_genres(): 
    return (top10genres.to_json())

@app.route('/data/get/sales', methods=['GET']) 
def get_sales(): 
    return (sales.to_json())

@app.route('/data/get/equal/<data_name>/<column>/<value>', methods=['GET']) 
def get_data_equal(data_name, column, value):
    data_name = sales
    #provide the name of data which is in this case, sales
    mask = data_name[column] == value
    #subset sales based on the column and then it must be equal to some value that is specified (Conditional subsetting)
    #value must all be string or integer
    #if integer, must put int(value)
    data_name = data_name[mask]
    #Conditional subsetting, save it in the original data
    return (data_name.to_json())

if __name__ == '__main__':
    app.run(debug=True, port=5000)