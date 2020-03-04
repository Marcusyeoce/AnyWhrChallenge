import bs4
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

# method that we can use to define the filter 
# can be a minimum number of ratings etc

class AttractionFilter:

    minimum_ratings = 0.0
    minimum_reviews = 0

    def __init__(self, minimum_ratings, minimum_reviews):
        self.minimum_ratings = minimum_ratings
        self.minimum_reviews = minimum_reviews

    def set_minimum_ratings(self, ratings):
        minimum_ratings = ratings

    def set_minimum_reviews(self, reviews):
        minimum_reviews = reviews

    def checkAttraction(self, ratings, reviews):
        if (ratings >= self.minimum_ratings) & (reviews >= self.minimum_reviews):
            return True
        else: 
            return False

def readPage(url):
    uClient = uReq(url)
    continent_html = uClient.read()
    uClient.close()
    return continent_html

# create a dictionary 
continents_url = {}

# add links for the various continents into the dictonary, such that we can simply add more links here if we want to expand our scope 
continents_url['Asia'] = 'https://www.tripadvisor.com.sg/Attractions-g2-Activities-Asia.html'
#continents_url['Europe'] = 'https://www.tripadvisor.com.sg/Attractions-g4-Activities-Europe.html'
#continents_url['Africa'] = 'https://www.tripadvisor.com.sg/Attractions-g6-Activities-Africa.html'

# creating a file to write the data to
filename = "tourist_attractions.csv"
f = open(filename, "w")

# add header into file
headers = "continent, city, attraction name, ratings, reviews\n"
f.write(headers)

# define filter parameters
attraction_filter = AttractionFilter(4.5, 100)

# looping through the continents
for key in continents_url:

    # opening up connection, grabbing the page
    continent_html = readPage(continents_url[key])

    # storing the web page as a soup
    continent_soup = soup(continent_html, "html.parser")
    
    #identify continent
    continent_name = key
    
    # loop through pages on the continent to search for more cities

    # trip advisor is tricky to navigate as the layout for the first page of each continent is different from the other pages
    # search for all cities in the continent
    city_containers = continent_soup.findAll("div", {"class":"geo_name"})

    # loop for each city in the continent
    for city in city_containers:

        # get city name
        city_temp = city.find('a').text.split()
        city_name = city_temp[0]

        # get link to city attractions page
        #city_url = city.find('a').get('href')
        #print(city_url)

        # link is currently hardcoded as I'm not sure how to convert a relative link to an absolute link
        city_url = 'https://www.tripadvisor.com.sg/Attractions-g298184-Activities-a_allAttractions.true-Tokyo_Tokyo_Prefecture_Kanto.html'
        city_html = readPage(city_url)
        city_soup = soup(city_html, "html.parser")
        

        # get last page for attractions in city so loop knows when to stop
        page_num_containers = city_soup.find("div", {"class":"pageNumbers"})
        pages = page_num_containers.findAll(('a'))
        max_page = int(pages[-1].text)

        # initialize current page as 1
        current_page = 1
        
        # traverse the pages for attractions in the city
        while current_page <= max_page:

            city_soup = soup(city_html, "html.parser") 
            attraction_container = city_soup.findAll("div", {"class":"flexible"})
            #attraction_container = city_soup.findAll("div", {"class":"tracking_attraction_title listing_title"})
            
            # get the attributes for each attraction
            for attraction in attraction_container:
                # get attraction name
                attraction_name_container = attraction.find("div", {"class":"tracking_attraction_title listing_title"})
                attraction_name = attraction_name_container.find('a').text

                # get attraction ratings
                attraction_ratings_container = attraction.find("span", {"class": lambda L: L and L.startswith('ui_bubble_rating')})
                attraction_ratings = attraction_ratings_container['alt'].split()
                num_ratings = float(attraction_ratings[0])

                # get attraction reviews
                attraction_reviews_container = attraction.find("span", {"class":"more"})
                attraction_reviews = attraction_reviews_container.find('a').text.split()
                num_reviews = int(attraction_reviews[0].replace(',', ''))

                # check if meets the condition of filter and write it to file
                if attraction_filter.checkAttraction(num_ratings, num_reviews):
                    f.write(continent_name + ", " + city_name + ", " + attraction_name.replace(",", "|") + ", " + str(num_ratings) + ", " + str(num_reviews) + "\n")
                    print(attraction_name)
                    print(num_ratings)
                    print(num_reviews)
        
            # increment current_pages by one, and look for the next page to navigate to
            # search for component with text == current_page to get link to next page
            current_page += 1
            city_html = ''

f.close()
