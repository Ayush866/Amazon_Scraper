import numpy as np
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os
import pandas as pd
baseurl = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1"

#Function to scrape Product_url,product_price,product_name,product_rating,product_num_reviews
def scraper(baseurl):
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    driver.get(baseurl)
    # time.sleep(300)
    products = []
    page = 0
    #this code will extract all the product name ,product price, product_reviews from the list of products
    for i in range(1, 21):
        page += 1
        for element in driver.find_elements(By.CLASS_NAME, 'a-price-whole'):
            try:
                product_name = element.find_element(By.XPATH, "../../../../../../../../..//h2").text
                if not product_name: continue
                # print(product_name)

                product_url = element.find_element(By.XPATH, "../../..").get_attribute("href")
                if not product_url: continue
                # print(product_url)

                product_price = element.find_element(By.XPATH, "../../../..").text.split(" ")[0]
                # print(product_price)
                product_rating = float(element.find_element(By.XPATH,
                                                            "../../../../../../../../..//span[contains(@aria-label, '5 stars')]").get_attribute(
                    'aria-label').split(" ")[0])
                # print(product_rating)
                product_num_reviews = int(element.find_element(By.XPATH,
                                                               "../../../../../../../../..//span[contains(@aria-label, '5 stars')]").find_element(
                    By.XPATH, "..").text.replace(",", ""))
                # print(product_num_reviews)
                products.append({
                    "product_url": product_url,
                    "product_name": product_name,
                    "product_price": product_price,
                    "product_rating": product_rating,
                    "product_num_reviews": product_num_reviews,
                    "page": page
                })
            except Exception as e:
                pass
        button = driver.find_element(By.CLASS_NAME, "s-pagination-next")
        button.click()
        time.sleep(3)

    # driver.quite
    df = pd.DataFrame(products)
    df.to_csv("scraper.csv", index=False)
    return df

#this function will hit the url that we got from above function and extract other informations
def scrape_product_info(url):

    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    driver.get(url)

    # Extract product description
    description = []
    for element in driver.find_elements(By.XPATH, "//li[@class='a-spacing-mini']"):
        try:
            des = element.find_element(By.XPATH, ".//span[@class='a-list-item']").text
            description.append(des)
        except Exception as e:
            pass
    if len(description)==0:
        description = np.NAN
    # Extract ASIN and manufacturer details
    asin = ""
    manufacturer_name=''
    for element in driver.find_elements(By.XPATH, "//div[@class='a-column a-span6 a-span-last']"):
        try:
            asin_name = element.find_element(By.XPATH, ".//th[@class='a-color-secondary a-size-base prodDetSectionEntry']").text
            if asin_name == "ASIN":
                asin = element.find_element(By.XPATH, ".//td[@class='a-size-base prodDetAttrValue']").text
                break
        except Exception as e:
            pass
    if not asin:
        try:
            for element in driver.find_elements(By.XPATH,
                                                "//*[@id='detailBullets_feature_div']/ul/li[5]/span/span[1]/following-sibling::span"):
                asin = element.text
        except:
            pass


    i = 0
    manufacturer = []
    for element in driver.find_elements(By.XPATH, "//td[@class='a-size-base prodDetAttrValue']"):
        try:
            i += 1
            manufacturer_name = element.text
            manufacturer.append(manufacturer_name)
            if i == 2:
                break
        except Exception as e:
            pass
    if not asin:
        try:
            for element in driver.find_elements(By.XPATH,
                                                "//*[@id='detailBullets_feature_div']/ul/li[4]/span/span[1]/following-sibling::span"):
                manufacturer_name = element.text
        except:
            pass
    # Extract product information
    product_info = []
    for element in driver.find_elements(By.XPATH, "//td[@class='apm-top']"):
        try:
            product = element.find_element(By.XPATH, ".//h4[@class='a-spacing-mini']").text
            p_tag = element.find_element(By.XPATH, ".//h4[@class='a-spacing-mini']/following-sibling::p")
            p_text = p_tag.text
            product_info.append({"Product": product, "Additional Info": p_text})
        except Exception as e:
            pass
    if not product_info:
        try:
            for element in driver.find_elements(By.XPATH, "//*[@id='productDescription']/p/span"):
                product_info = element.text
        except:
            pass
    driver.quit()

    return {
        "Description": description,
        "ASIN": asin,
        "Manufacturer": manufacturer_name,
        "Product Info": product_info
    }


if __name__=="__main__":
    df=(scraper(baseurl))
    #df=pd.read_csv(r"E:\Amazon_scraper\scraper.csv")
    #print(df.head())
    df1 = pd.DataFrame(columns=['Description', 'ASIN', 'Manufacturer', 'Product Info'])
    counter = 0
    for i in df["product_url"]:
        counter += 1
        # url = "https://www.amazon.in/FUR-JADEN-Leatherette-Polypropylene-DUFF05/dp/B07M9BRCQ5/ref=sr_1_6?crid=2M096C61O4MLT&keywords=bags&qid=1697528916&sprefix=ba%2Caps%2C283&sr=8-6&th=1"

        product_data = scrape_product_info(i)
        df1.loc[len(df1)] = product_data

        if counter == 201:
            break
    df1.to_csv("second_scraper.csv", index=False)



