#Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
#from webdriver_manager.chrome import ChromeDriverManager
import datetime as dt
import requests

def scrape_all():
# Set the executable path and initialize Splinter
#executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', executable_path="chromedriver",headless=True)
    
    news_title, news_paragraph= mars_news(browser)
    hemisphere_image_urls= hemisphere(browser)
    # Run all scraping functions and store results in dictionary 
    data={
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemisphere_image_urls,
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')
    try:
        #slide_elem looks for <ul /> tags and descendents <li />
        # the period(.) is used for selecting classes such as item_list
        slide_elem= news_soup.select_one('ul.item_list li.slide')

        # Chained the (.find) to slide_elem which says this variable holds lots of info, so look inside to find this specific entity
        # Get Title
        news_title=slide_elem.find('div', class_= 'content_title').get_text()
        # Get article body
        news_p= slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None,None

    return news_title, news_p
    


def featured_image(browser):
    # ### JPL Space Images Featured Image
    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')
    #img_soup
    try:
        # find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
        #img_url_rel
    except AttributeError:
        return None
    # Use the base url to create an absolute url
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'
    return img_url


# ### Mars Facts
def mars_facts():
    try:
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]
        #df.head()
    except BaseException:
        return None
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)
    df

    return df.to_html()


# # D1: Scrape High-Resolution Mars’ Hemisphere Images and Titles

# ### Hemispheres
def hemisphere(browser):
    # 1. Use browser to visit the URL 
    url = 'https://data-class-mars-hemispheres.s3.amazonaws.com/Mars_Hemispheres/index.html'

    browser.visit(url)


    
    response = requests.get(url)
    test  = soup(response.text,'html.parser')
    #item1 = test.find_all('div', class_='item')


    #main_url  = 'https://data-class-mars-hemispheres.s3.amazonaws.com/Mars_Hemispheres/'
    #title = test.find('h3').text
    #part_img = test.find('a',class_='itemLink product-item')['href']
    #browser.visit(main_url+part_img)

    #print(main_url+part_img)

    # 2. Create a list to hold the images and titles.
    main_url = 'https://data-class-mars-hemispheres.s3.amazonaws.com/Mars_Hemispheres/'
    hemisphere_image_urls = []
    items = test.find_all('div', class_ ='item')
    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    for item in items:
        #hemispheres = {}
        title = item.find('h3').text
        part_img_url = item.find('a', class_= 'itemLink product-item')['href']
        browser.visit(main_url+part_img_url)
        part_img_html = browser.html
        test = soup(part_img_html,'html.parser')
        img_url = main_url+test.find('img',class_='wide-image')['src']
        hemisphere_image_urls.append({'title':title,'img_url':img_url})



# 4. Print the list that holds the dictionary of each image url and title.
    return hemisphere_image_urls   

# 5. Quit the browser
if __name__== "__main__":
    # If running as script, print scrapped data
    print(scrape_all())



