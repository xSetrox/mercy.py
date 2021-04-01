# mercy.py
<a href="url"><img src="https://i.imgur.com/nCJopUE.png" align="center" height="100" width="100" ></a>
python 3.8 mercy college directory searching for humans

## why
the mercy college directory only lets you search by name. this is extremely limiting and makes the directory utterly useless. so, i wrote my own
system to search the directory however i want.

## how
there are 2 parts of how this is done. the first is the database 'building'. i employ web scraping using beautifulsoup4 and requests, then store all those results into a sqlite3 database.  
the second is the search feature, which simply runs SQL "like" queries against the database to search through it, and then we use prettytable to write the results out neatly in console (if any)  
the database and table is created automatically upon your first run, so don't worry

## usage
this is a command-line based tool, so all your work will be done in there.  
the base usage is `python main.py`, and the args are `-build` as well as a multi-word argument, your query.  
so if you want to search for john doe you would simply type `python main.py john doe`  
but before you can search you need to 'build' your database (or populate it with rows from the directory).  
to do this, type `python main.py -build`

## setup
you just need to install requirements, so cd into the project directory and type `pip install -r requirements.txt`  
for the junkies that like to see all the requirements for some reason though, here:  
```
prettytable==2.0.0
requests==2.25.1
beautifulsoup4==4.9.3
```
