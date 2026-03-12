from bs4 import BeautifulSoup

# Finds the unread emails along with organizing email data to be plugged into an LLM. 

def get_unread_emails(html):
    unread_emails = []
    soup = BeautifulSoup(html, "lxml")
    email_table = soup.find("div", class_="Cp").div.table
    print(email_table)
    return 0