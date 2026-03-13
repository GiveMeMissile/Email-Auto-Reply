from bs4 import BeautifulSoup

# Function which finds important data for each unread email and returns a list with all of the information for each email. 
def get_unread_emails(html):
    unread_emails_info = []
    soup = BeautifulSoup(html, "lxml")
    unread_emails = soup.find_all("tr", class_="zA zE")
    
    for email in unread_emails:
        email_title = email.find("td", class_="yX xY ulKHrd").find("div", class_="yW").span.span.text
        info = email.find("div", class_="xT")
        email_subject = info.find("span", class_="bqe").text
        email_info = info.find("span", class_="y2").text
        unread_emails_info.append((email_title, email_subject, email_info))

    return unread_emails_info

def proccess_email_html(html):
    soup = BeautifulSoup(html, "lxml")
    email_text = soup.text.replace("\n", " ")
    email_text = email_text.split()
    text = ""
    for part in email_text:
        text += part + " "
    email_text = text

    return email_text
