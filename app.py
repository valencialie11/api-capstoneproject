from flask import Flask, request 
import pandas as pd 
import sqlite3
app = Flask(__name__) 

conn = sqlite3.connect("data_input/chinook.db")
songs = pd.read_sql_query('''SELECT t.name as Song, g.name as Genre, a.title as Album,
ar.name as ArtistName, m.name as MediaTypes, t.unitprice as UnitPrice, t.Composer,
i.CustomerId, c.FirstName, c.LastName, ii.Quantity,
i.InvoiceDate,i.Billingcity as City,i.billingCountry as Country
from tracks t
left join playlist_track on playlist_track.trackid = t.name
left join playlists p on playlist_track.playlistid = p.playlistid
left join media_types m on m.mediatypeid = t.mediatypeid
left join genres g on g.genreid = t.genreid
left join albums a on a.albumid = t.albumid
left join artists ar on ar.artistid = a.artistid
left join invoice_items ii on ii.trackid = t.trackid
left join invoices i on ii.invoiceid = i.invoiceid
left join customers c on i.customerid = c.customerid''', conn)

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
    <h1> Documentation of Endpoints: </h1>
    <h2> Static Endpoints </h2>
    <ol>
        <li>
            <p> /, method = POST </p>
            <p> Base endpoint that is interactive and let's the user compute their name and favourite song. </p>
        </li>
        <li>
            <p> /docs, method = GET </p>
            <p> Documentation about the use of API. </p>
        </li>
        <li>
            <p> /data/get/catalogue, method = GET </p>
            <p> To show the whole list of songs. </p>
        </li>
        <li>
            <p> /data/get/top10songs, method = GET </p>
            <p> To show top 10 songs from the number of sales. </p>
        </li>
        <li>
            <p> /data/get/top10artists, method = GET </p>
            <p> To show top 10 artists from the number of sales. </p>
        </li>
        <li>
        <p> /data/get/top10genres, method = GET </p>
            <p> To show top 10 genres from the number of sales. </p>
        </li>
    </ol>
    <h2> Dynamic Endpoint </h2>
    <ol>
        <li>
            <p> /data/get/sales , method = GET </p>
            <p> To show the whole data on sales </p>
            <p> To filter: </p>
            <ul style="list-style-type:disc;">
                <li> city: to filter based on the city where the purchase of the songs are made, for example:
                        /data/get/sales?city=Rome</li>
                <li> country: to filter based on the country where the purchase of the songs are made, for example:
                        /data/get/sales?country=Canada</li>
                <li> genre: to filter based on the genre of the songs, for example:
                        /data/get/sales?genre=Blues</li>
                <li> artist: to filter based on the artists of the songs, for example:
                        /data/get/sales?artist=U2</li>
                <li> year: to filter based on the year when the purchase of the songs are made, for example:
                        /data/get/sales?year=2014</li>
                <li> col : to filter based on the columns you want, for example:
                        /data/get/sales?col=[Song,Genre,Year,ArtistName,Album]</li>
            </ul>
            <p> To combine different combinations of the filters above, you can use &amp, for example:
                    /data/get/sales?year=2011&genre=Reggae </p>
        </li>
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
def sales():
    city = request.args.get('city')
    country = request.args.get('country')
    genre = request.args.get('genre')
    artist = request.args.get('artist')
    year = request.args.get('year')
    col = request.args.get('col')

    #tuple for name of column
    column = []
    #tuple for ==
    equal = []
    #tuple for condition specified in link
    condition = []

    if (city == None) & (country == None) & (genre == None) & (artist == None) & (year == None):
        return (sales.to_json())
    
    if city:
        column.append('City')
        equal.append('==')
        condition.append(city)

    if country:
        column.append('Country')
        equal.append('==')
        condition.append(country)

    if genre:
        column.append('Genre')
        equal.append('==')
        condition.append(genre)

    if artist:
        column.append('ArtistName')
        equal.append('==')
        condition.append(artist)
    
    if year:
        column.append('Year')
        equal.append('==')
        condition.append(int(year))
        #To ensure that the year that is typed in is integer



if __name__ == '__main__':
    app.run(debug=True, port=5000)