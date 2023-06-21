from utils import process_request, save_response
import os
from bs4 import BeautifulSoup as bs


class Epopress:

    @staticmethod
    def get_headers():
        return {
        'Accept': '*/*',
        'Accept-Language': 'en-GB,en;q=0.5',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'ARRAffinity=f5c1947968dba7c2a95b655202fe24cfbe4f782d26e36d6f57faab3445e49a64; ARRAffinitySameSite=f5c1947968dba7c2a95b655202fe24cfbe4f782d26e36d6f57faab3445e49a64; ASP.NET_SessionId=402m1wytg0kp0qgvgn3fyxl4; fullPageViews=3; ARRAffinity=f5c1947968dba7c2a95b655202fe24cfbe4f782d26e36d6f57faab3445e49a64; ARRAffinitySameSite=f5c1947968dba7c2a95b655202fe24cfbe4f782d26e36d6f57faab3445e49a64; ASP.NET_SessionId=gj5qx4ffzwupzx150hgbnhfy',
        'Origin': 'https://xpopress.com',
        'Referer': 'https://xpopress.com/vendor/search',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-GPC': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Brave";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
        }

    def get_details(self, url):
        payload = {}
        try:
            response = process_request("POST", url, headers=Epopress.get_headers(), payload=payload)
        except Exception:
            return {}
        soup = bs(response.content, "html.parser")
        try:
            company = soup.find("div", class_="container sc-top fixed-profile-info")
            company_name = company.h1.text
        except Exception:
            company_name = None
        try:
            location = soup.find("div", class_="sc-location").text
        except Exception:
            location = None
        try:
            contact = soup.find("div", class_="sc-details").text
            phone = contact.split("\r")[2].split("\n")[1].replace(" ", "")
        except Exception:
            phone = None
        try:
            name = contact.split("\r")[1].split("\n")[1]
        except Exception:
            name = None
        try:
            email = contact.split("\r")[2].split("\n")[2]
        except Exception:
            email = None
        try:
            about_company = soup.find("div", class_="sc-details").text.split("More About This Company:\n")
            company_details = about_company[1]
        except Exception:
            company_details = about_company[0]

        products = soup.find_all("div", id="goto-products-area")
        product_details = products[0].text.replace("\nProducts:\n", "").replace("\n", "")
        images = soup.find_all("div", class_="col-sm-12 sc-details middle-page-banner")
        image_lists = []
        for image in images:
            image_lists.append(image.img.get("src"))
        company_info = {
            "company_name": company_name,
            "location": location,
            "name": name,
            "phone": phone,
            "email": email,
            "about_company": company_details,
            "product_details": product_details,
            "images": image_lists
        }
        return company_info

    def get_url_lists(self):
        url = "https://xpopress.com/Vendor/RunSearch"
        payload = "vendor=+&product=&show=&showcase="
        response = process_request("POST", url, headers=Epopress.get_headers(), payload=payload)
        soup = bs(response.content, "html.parser")
        urls = soup.find_all("a", class_="vendor-result-link")
        product_details = []
        count = 0
        for url in urls:
            detail_url = f"https://xpopress.com{url.get('href')}"
            product_details.append(self.get_details(detail_url))
            if count == 1500:
                return product_details
            count += 1
        return product_details

if __name__ == '__main__':
    epopress = Epopress()
    details = epopress.get_url_lists()
    save_response(details, "details.json", os.path.join(os.path.dirname(__file__), "Data"))