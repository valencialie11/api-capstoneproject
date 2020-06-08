# API Capstone Project
I did not do this project as part of my course's requirements but I did this during my free time (whereas I did my webscraping for my Capstone Project).
However, I did use my academy's resources as guidelines to help me understand what API is all about and how to go about making simple static and dynamic endpoints. Since I learnt about sql query recently, I thought it would be fitting for the data to be taken directly from a database.
I really learnt a lot through this mini project, especially because I did this alone without any teacher or mentor helping me. Though there are still a lot of things I don't know about API, as of now, I'm satisfied with the endpoints I made!

# Dependencies:
- pandas
- sqlite3
- request
- flask

# Documentation of Endpoints

## Static Endpoints:

1. Base endpoint that is interactive and let's the user compute their name and favourite song:

/form, method = POST

2. Documentation about the use of API:

/docs, method = GET

3. To show the whole list of songs:

/data/get/catalogue, method = GET

4. To show top 10 songs from the number of sales:

/data/get/top10songs, method = GET

5. To show top 10 artists from the number of sales:

/data/get/top10artists, method = GET

6. To show top 10 genres from the number of sales:

/data/get/top10genres, method = GET

## Dynamic Endpoints:
1. To show the whole data on sales

/data/get/sales , method = GET

2. To filter based on your desired conditions:

/data/get/equal/data_name]/column]/[value], where [data_name] is sales.

  For example:

  - When you want to filter based on the country where the purchase of the songs are made, you can enter:

  /data/get/equal/sales/Country/Germany

  - When you want to filter based on the year of the purchase of the songs, you can enter:
  /data/get/equal/sales/Year/2009

  - When you want to filter based on the artist, you can enter:
  /data/get/equal/sales/ArtistName/U2

  - When you want to filter based on the genre, you can enter:
  /data/get/equal/sales/Genre/Classical

  And so on...

3. To filter using different combinations:

/data/get/equal/multiple/[data_name1]/[column1]/[value1]/[column2]/[value2], where [data_name1] is sales.

For example:
/data/get/equal/multiple/sales/Genre/Rock/Year/2009 to filter out rock songs that was bought in 2009.

4. To filter out based on columns:

/data/get/equal/columns/[data_name2]/[column3]/[column4]/[column5], where [data_name2] is sales.

For example:
/data/get/equal/columns/sales/ArtistName/MediaTypes/Genre to filter based on these 3 columns.
