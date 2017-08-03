import sys, os
from selenium import webdriver
from bs4 import BeautifulSoup as bs

class NaverBlog():
    def __init__(self):
        self.blog_ids = []
        self.id = ''
        self.password = ''
        self.chromedriver_path = ''
        self.keyword = ''
        self.max_page = 0
        self.contents= ''
        self.send_interval = 0
        self.driver = None

    def init(self):
        self.do_init()
    def do_init(self):
        with open("./config.txt", "r") as f:
            lines = f.readlines()
        for line in lines:
            line_split = line.splitlines()[0].split('=')
            if line_split[0] == 'id':
                self.id = line_split[1]
            elif line_split[0] == 'password':
                self.password = line_split[1]
            elif line_split[0] == 'chromedriver_path':
                self.chromedriver_path = line_split[1]
            elif line_split[0] == 'keyword':
                self.keyword = line_split[1]
            elif line_split[0] == 'max_page':
                self.max_page = line_split[1]
            elif line_split[0] == 'contents':
                self.contents = line_split[1]
            elif line_split[0] == 'send_interval':
                self.send_interval = int(line_split[1])
    def print_init(self):
        print('id = ' + self.id)
        print('password = ' + self.password)
        print('chromedriver_path = ' + self.chromedriver_path)
        print('keyword = ' + self.keyword)
        print('max_page = ' + self.max_page)
        print('contents = ' + self.contents)
        print('send_interval = ' + self.send_interval)
    def parsing(self):
        self.driver = webdriver.Chrome(self.chromedriver_path)
        self.driver.implicitly_wait(3)
        self.blog_ids = []
        num = 1
        for i in range(0, int(self.max_page)):
            url = 'https://m.search.naver.com/search.naver?where=m_blog&sm=mtb_pge&query=' + self.keyword +'&display=15&st=sim&nso=&start=' + str(num)
            print(url)
            self.blog_ids = self.blog_ids + self.do_parsing(url)
            num = num + 15
        self.driver.quit()
    def do_parsing(self, url):
        blog_ids = []
        self.driver.get(url)
        elem = self.driver.find_elements_by_class_name('lst_total')
        source_code = self.driver.page_source
        plain_text = source_code
        soup = bs(plain_text, "html5lib")
        lst_total = soup.find("ul", { "class" : "lst_total" })

        for a in lst_total.find_all('a', href=True):
            blog_url = a['href']
            if blog_url.find('naver') > 0:
                blog_id = blog_url.split('/')[-2]
                blog_ids.append(blog_id)

        return blog_ids

    def send_gift(self):
        self.driver = webdriver.Chrome(self.chromedriver_path)
        self.driver.implicitly_wait(3)
        self.naver_login()
        self.do_send_gift()
        self.driver.quit()

    def naver_login(self):
        self.driver.get('https://nid.naver.com/nidlogin.login')
        self.driver.find_element_by_name('id').send_keys(self.id)
        self.driver.find_element_by_name('pw').send_keys(self.password)
        self.driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()
        self.driver.implicitly_wait(2)

    def do_send_gift(self):
        for blog_id in self.blog_ids:
            print(blog_id)
            self.driver.get('http://item2.naver.com/FontDetail.nhn?itemSeq=994265')
            self.driver.execute_script('javascript:clickOnGift()')
            driver_new = self.driver.window_handles[1]
            driver_origin = self.driver.window_handles[0]
            self.driver.switch_to_window(driver_new)
            self.driver.find_element_by_name('receiveuserid').send_keys(blog_id)
            self.driver.find_element_by_name('sendmessage').send_keys(self.contents)
            self.driver.find_element_by_xpath('//*[@id="footer"]/input').click()
            self.driver.close()
            self.driver.switch_to_window(driver_origin)
            self.driver.implicitly_wait(self.send_interval)

    def do_parsing_send_gift(self):
        self.init()
        self.print_init()
        self.parsing()
        self.send_gift() 

naver = NaverBlog()
naver.do_parsing_send_gift()
