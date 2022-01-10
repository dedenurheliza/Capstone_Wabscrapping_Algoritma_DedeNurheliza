from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

# Creating the lists we want to write into
# define for array 
title = []
rate = []
metascore = []
vot= []

#array for looping data 
#total movie in one layer is 50 movies, 
#for the next page, it must loop (from 1, 51,101, etc)
numb = np.arange(1, 202, 50)

#looping from page 1,51,101,151 and 201
#get data title, rate, metascore and vot from IMDb 

for num in numb:
    #get data from web
    num = requests.get('https://www.imdb.com/search/title/?release_date=2021-01-01,2021-12-31&start=' + str(num) + '&ref_=adv_nxt')
    soup = BeautifulSoup(num.text, 'html.parser')
    
    # get information from all part of movie (include title, vote, etc)
    # in div class lister-item mode-advance
    movie_div = soup.find_all('div', class_='lister-item mode-advanced')
    
    for i in movie_div:
        # Scraping title of movie
        name = i.h3.a.text #get data from h3
        title.append(name) #append data to array title

        # Scraping the rate of movie
        imdb=i.find('div', class_='inline-block ratings-imdb-rating') #get data from div
        if imdb is not None:
            imdb_rating=float(imdb.text) #get data text and change to float type data
        rate.append(imdb_rating) #append data to array rate
        
        # Scraping the metascore
        #get data from span
        #metascore for several movie is empty, so it must define, if empty, just write (-)
        m_score = float(i.find('span', class_='metascore').text) if i.find('span', class_='metascore') else '-' 
        metascore.append(m_score) #append data to array metascore
        
        # Scraping votes 
        vote=i.find('p', class_='sort-num_votes-visible') #get data from p
        if vote is not None:
            votes=vote.text.split()[1]
        vot.append(votes) #append data to array vot

#save to DataFrame
movie= pd.DataFrame({'Movie Title':title, 
                       'IMDb_rating':rate, 
                       'Metascore':metascore,
                       'Vote':vot})

movie['Metascore'] = movie['Metascore'].replace('-', np.nan)
movie['Metascore'] = movie['Metascore'].astype(float)

#change dtype of Vote
movie['Vote'] = movie['Vote'].str.replace(',', '') #change , to .
movie['Vote'] = movie['Vote'].astype(float) #change to float

basetop=movie

basetop2 = movie.groupby('Movie Title').agg({
    'Metascore': 'mean',
    'IMDb_rating': 'mean'
}).sort_values(by='Metascore',ascending=False).dropna().sort_values(by='IMDb_rating',ascending=False).reset_index()

d=movie['Vote']>150000
movie['Movie Title']=movie['Movie Title'][d]
movie.sort_values('Movie Title',inplace=True)

basetop3 = movie.groupby('Movie Title').agg({
    'Metascore': 'mean',
    'IMDb_rating': 'mean'
}).sort_values(by='Metascore',ascending=False).dropna().sort_values(by='IMDb_rating',ascending=False).reset_index()
basetop3.head(7)

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{movie["IMDb_rating"].mean().round(2)}' #be careful with the " and ' 

	# generate plot1
	fig = plt.figure(figsize=(8,6))
	title_ = basetop['Movie Title'][0:6]
	rate_ = basetop['IMDb_rating'][0:6]
	plt.barh(title_,rate_,color='orange')
	plt.xticks(fontsize=14)
	plt.yticks(fontsize=13)
	plt.xlabel(r'Rating',fontsize=16)
	plt.title('Top 7 Movies from Web \n Default \n',fontsize=18)
	plt.show() 

	# generate plot2
	title_ = basetop2['Movie Title'][0:6]
	rate_ = basetop2['IMDb_rating'][0:6]
	plt.barh(title_,rate_,color='g')
	plt.xticks(fontsize=14)
	plt.yticks(fontsize=13)
	plt.xlabel(r'Rating',fontsize=16)
	plt.title('Top 7 Movies from Web \n sort by Rate \n',fontsize=18)
	plt.show()
	
	# generate plot3
	title_ = basetop3['Movie Title'][0:6]
	rate_ = basetop3['IMDb_rating'][0:6]
	plt.barh(title_,rate_,color='brown')
	plt.xticks(fontsize=14)
	plt.yticks(fontsize=13)
	plt.xlabel(r'Rating',fontsize=16)
	plt.title('Top 7 Movies from Web \n sort by amount of Voter (>150.000) and Rate \n',fontsize=18)
	plt.show()
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)