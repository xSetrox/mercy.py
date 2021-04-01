import argparse
import sqlite3
import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable

# creates database if not existent, otherwise creates
conn = sqlite3.connect('accounts.db')
# creates table if it does not exist, to prepare the database
conn.execute("CREATE TABLE IF NOT EXISTS accounts (name, position, email, phone, office,address)")
conn.commit()


def scrape_and_build():
    # while loop, only because we dont know how many pages we will encounter
    cur_page = 0
    new = 0
    existing = 0
    # url base to start with
    dir_link = 'https://www.mercy.edu/directory?name=&page='
    print('Scraping operation has started')
    while True:
        page = requests.get(dir_link + str(cur_page)).text
        soup = BeautifulSoup(page, 'lxml')
        listings = soup.find_all('div', {'class': 'flex-2/3 sm:pr-60 mb-15 sm:mb-0'})
        # stop loop if nothing found, should stop at around page 189 at the time im writing this
        # or, will stop if mercy screws up, and then data wont be messed with
        if not listings:
            print(
                f'Database building has finished. {new} new listings were added and {existing} existing were modified')
            break
        for l in listings:
            # get ready for some awfully long lines that violate pep-8 E501 because the web designer doesnt like making custom css
            # we are going to need to use try and except because for some reason the listings are extremely inconsistent
            name = l.find('a', {
                'class': 'font-playfair font-bold text-blue-400 text-xl lg:text-4xl leading-tight shadow-yellow-under-md lg:shadow-yellow-under-xl hover:text-black hover:bg-yellow transition-colors duration-200'}).span.text
            # sometimes even position is blank iirc. crazy, right?
            try:
                position = l.find('span', {'class': 'block font-muli text-sm text-gray-800 mt-10'}).text.replace('\n',
                                                                                                                 ' ')
            except AttributeError:
                position = 'Not given'
            # some dont even have so much as an *email* listed. the more i look into this the more i wanna die
            try:
                # now they decide to use custom classes, really odd
                email = l.find('div', {'class': 'field--name-field-email'}).a.text
            except AttributeError:
                email = 'Not given'
            try:
                phone = l.find('div', {'class': 'field--name-field-phone'}).a.text
            except AttributeError:
                phone = 'Not given'
            # these sometimes have multiple parts, im just going to merge them and replace newlines with spaces i guess
            try:
                office = l.find('div', {'class': 'field--name-field-office'}).text.replace('\n', ' ').strip()
            except AttributeError:
                office = 'Not given'
            # oh yeah and sometimes some listings have their office address, which is redundant i think but whatevs
            try:
                addr = l.find('div', {'class': 'field--name-field-office-address'}).p.stripped_strings
                addr = ' '.join(addr) if addr else ''
                # sometimes address is literally just ','. this is how it is on the website and its not my code's fault
                # no clue how this happens, but we can filter it out
                if addr == ',':
                    addr = 'Not given'
            except AttributeError:
                addr = 'Not given'
            # first check if name is already in database
            returned = conn.execute("SELECT * FROM accounts WHERE name=?", (name,)).fetchall()
            if returned:
                print(name, 'is already in the database, modifying data instead')
                existing += 1
                conn.execute(
                    'UPDATE accounts SET position = ?, email = ?, phone = ?, office = ?, address = ? WHERE name = ?',
                    (position, email, phone, office, addr, name))
            else:
                new += 1
                conn.execute("INSERT INTO accounts VALUES (?,?,?,?,?,?)", (name, position, email, phone, office, addr))
                print('Adding', name)
                conn.commit()
        cur_page += 1


def search_db_for(query):
    row_ct = conn.execute('SELECT COUNT(*) FROM accounts')
    if row_ct == 0:
        print(
            'Your database is empty! You need to populate it before you can search.\nRun the -build argument to do so.')
        return
    vis_query = query
    query = '%' + query + '%'
    # we're just not going to include address, not only because pretty much nobody has a specific one listed
    # that is more than just '555 broadway' or 'tarrytown',
    returned = conn.execute(
        "SELECT * FROM accounts WHERE name LIKE ? OR position LIKE ? OR email LIKE ? OR phone LIKE ? OR office LIKE ?",
        (query, query, query, query, query)).fetchall()
    if len(returned) < 1:
        print(f'No results found for \"{vis_query}\"')
        return
    head = ['Name', 'Position', 'Email', 'Phone', 'Office', 'Address']
    x = PrettyTable()
    x.field_names = head
    for l in returned:
        x.add_row(l)
    print(f'Results for {vis_query}:\n', x)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='mercy.py command line tool')
    parser.add_argument('-build', help='Scrapes the directory and adds all accounts to database', action='store_true')
    parser.add_argument('query', type=str, nargs='*', help='Information to search for (can be name, email, phone, etc)')
    args = parser.parse_args()
    if args.build:
        scrape_and_build()
    else:
        query = ' '.join(args.query)
        search_db_for(query)
