import sys, os, time, signal
from subprocess import check_output
check_output("./Scripts/pip install beautifulsoup4", shell=True)

try:
    from selenium import webdriver
except ImportError, e:
    check_output("./Scripts/pip install beautifulsoup4", shell=True)
    from selenium import webdriver

try:
    from selenium.webdriver.common.alert import Alert
except ImportError, e:
    print('Error : rom selenium.webdriver.common.alert import Alert')

try:
    from bs4 import BeautifulSoup as bs
except ImportError, e:
    check_output("./Scripts/pip install beautifulsoup4", shell=True)
    from bs4 import BeautifulSoup as bs




def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

class NaverBlog():
    def __init__(self):
        self.blog_ids = []
        self.id = ''
        self.password = ''
        self.chromedriver_path = ''
        self.keyword = ''
        self.max_page = 0
        self.contents= ''
        self.driver = None
        self.send_interval = 0
        self.file_path = ''
        self.init_initialized = False

    def start(self):
        self.print_command()
        while True:
            command = input('Select Command :')
            if command == '':
                command = 99
            else:
                command = int(command)

            if command == 0:
                print('================ Do Quit ================')
                return
            elif command == 1:
                print('================ Do Set configuration ================')
                self.init()
                self.print_init()
                self.init_initialized = True
            elif command == 2:
                print('================ Do Collect naver ID ================')
                if self.check_init() == False:
                    continue
                self.parsing()
                print('Number of collected IDs : ' + str(len(self.blog_ids)))
                print('')
                print('')
            elif command == 3:
                print('*================ Do Send gift up to 50 ID ================')
                if self.check_init() == False:
                    continue
                self.send_gift()
            elif command == 4:
                print('================ Do Send note up to 500 ID ================')
                if self.check_init() == False:
                    continue
                self.send_note()
            elif command == 5:
                print('================ Show collected IDs ================')
                self.print_collected_ids()
            else:
                self.print_command()

    def print_command(self):
        print('================ MENU ================')
        print('1 : Set configuration')
        print('2 : Collect naver ID')
        print('3 : Send gift up to 50 ID')
        print('4 : Send note up to 500 ID')
        print('5 : Show collected IDs')
        print('0 : Quit')
        print('======================================')
        print('')

    def print_collected_ids(self):
        for blog_id in self.blog_ids:
            print(blog_id)
        print('total Ids : ' + str(len(self.blog_ids)))
    def check_init(self):
        if self.init_initialized == False:
            print('Please select command 1 first.')
        return self.init_initialized

    def init(self):
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
            elif line_split[0] == 'file_path':
                self.file_path = line_split[1]


    def print_init(self):
        print('keyword = ' + self.keyword)
        print('')
        print('id = ' + self.id)
        print('password = ' + self.password)
        print('chromedriver_path = ' + self.chromedriver_path)
        print('file_path = ' + self.file_path)
        print('max_page = ' + self.max_page)
        print('send_interval = ' + str(self.send_interval))
        print('contents = ' + self.contents)
        print('')

    def parsing(self):
        self.driver = webdriver.Chrome(self.chromedriver_path)
        self.driver.implicitly_wait(3)
        self.blog_ids = []
        num = 1
        for i in range(0, int(self.max_page)):
            url = 'https://m.search.naver.com/search.naver?where=m_blog&sm=mtb_pge&query=' + self.keyword +'&display=15&st=sim&nso=&start=' + str(num)
            try:
                self.blog_ids = self.blog_ids + self.do_parsing(url)
            except:
                print('Error - It is likely that there are no more pages to scan')
                print('')
                break
            num = num + 15
        self.blog_ids = list(set(self.blog_ids))
        self.save_file(self.keyword, len(self.blog_ids))
        self.driver.quit()

    def do_parsing(self, url):
        blog_ids = []
        self.driver.get(url)
        self.driver.set_window_size(0, 0)
        self.driver.set_window_position(0, 0)
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

    def save_file(self, keyword, nkeyword):
        path = self.file_path + keyword + '_' + str(nkeyword) + '.txt'
        f = open(path, 'w')
        for blog_id in self.blog_ids:
            f.write(blog_id+'\n')
        f.close()
        print('blog_ids saved to ' + path)

    def send_gift(self):
        self.driver = webdriver.Chrome(self.chromedriver_path)
        self.driver.implicitly_wait(3)
        self.do_naver_login()
        send_num = self.do_send_gift()
        print(str(send_num) + ' IDs completed')
        print('')
        self.driver.quit()

    def send_note(self):
        self.driver = webdriver.Chrome(self.chromedriver_path)
        self.driver.implicitly_wait(3)
        self.do_naver_login()
        self.do_send_note()
        print('Send note completed')
        print('')
        self.driver.quit()

    def do_naver_login(self):
        self.driver.get('https://nid.naver.com/nidlogin.login')
        self.driver.find_element_by_name('id').send_keys(self.id)
        self.driver.find_element_by_name('pw').send_keys(self.password)
        self.driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()
        try:
            driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/span[2]/a').click()
        except:
            pass
        self.driver.implicitly_wait(2)

    def do_send_gift(self):
        send_num = 0
        for blog_id in self.blog_ids:
            if send_num == 50:
                break
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
            self.driver.implicitly_wait(2)
            send_num = send_num + 1
        return send_num

    def do_send_note(self):
        send_ids = self.blog_ids
        self.driver.get('http://note.naver.com/#{"sHistoryFunction":"write","sWriteType":"new","oParameter":{"targetUserId":"","toMe":"0"},"sUrl":"/json/write/"}')
        while len(send_ids) != 0:
            num_id = 0
            send_id = ''
            while len(send_ids) != 0:
                if num_id == 10:
                    break
                send_id = send_id + send_ids.pop() + ','
                num_id = num_id + 1
            self.driver.find_element_by_xpath('//*[@id="who"]').clear()
            self.driver.find_element_by_xpath('//*[@id="writeNote"]').clear()
            self.driver.find_element_by_xpath('//*[@id="who"]').send_keys(send_id)
            self.driver.find_element_by_xpath('//*[@id="writeNote"]').send_keys(self.contents)
            self.driver.find_element_by_xpath('//*[@id="cont_fix_area"]/div[6]/div[1]/a[1]').click()
            while True:
                try:
                    alert = Alert(self.driver).text
                    time.sleep(1)
                    break
                except:
                    pass
            while True:
                try:
                    Alert(self.driver).accept()
                    break
                except:
                    pass
            time.sleep(self.send_interval)

naver = NaverBlog()
naver.start()
