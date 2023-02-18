from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from time import sleep, strftime
from random import randint
from bs4 import BeautifulSoup
import json

import simple_request
from logger import Log
from instatags import InstagramTags

__INSTAGRAM_URL__ = 'https://www.instagram.com/'
__INSTAGRAM_HASHTAGS_URL__ = __INSTAGRAM_URL__ + 'explore/tags/'
__ACTION_LOG_FILE__ = './logs/action.log'
__ERROR_LOG_FILE__ = './logs/error.log'

class InstaBot:
    def __init__(self):
        self.browser = None
        # it is used to be sure that just one post from profile will be used if there are more than one post for a profile in resuts.
        self.__current_profiles__ = []
        self.__black_list__ = ['tagneshan.ir', 'madaremoshtari', 'khaziran_ir']
        return

    def login(self, user_name, user_password, delay=10):
        self.browser = webdriver.Firefox(firefox_binary='/opt/firefox-dev/firefox')
        sleep(2)
        self.browser.get(__INSTAGRAM_URL__ + 'accounts/login/?source=auth_switcher')
        sleep(7)

        try:
            username = self.browser.find_element_by_name('username')
            username.send_keys(user_name)
            password = self.browser.find_element_by_name('password')
            password.send_keys(user_password)

            # login_button = self.browser.find_element_by_css_selector('#react-root > section > main > div > article > div > div:nth-child(1) > div > form > div:nth-child(3) > button')
            login_button = self.browser.find_element_by_xpath('/html/body/span/section/main/div/article/div/div[1]/div/form/div[4]/button')
            login_button.click()
            sleep(delay)
            Log(__ACTION_LOG_FILE__, True, 'login', user_name)
        except NoSuchElementException:
            Log(__ERROR_LOG_FILE__, True, 'login fields not found!')
            return False

        # check for successful login.
        try:
            self.browser.find_element_by_id('slfErrorAlert')
            self.browser = None
            return False
        except NoSuchElementException:
            return True

    def logout(self):
        # NOTE: it is not real logout!
        self.browser = None
        return
    
    def like_follow_comment_post(self, shortcode, like=True, follow=False, comment=None, delay=1):
        if self.browser is None:
            return

        try:
            self.browser.get(__INSTAGRAM_URL__ + 'p/' + shortcode + '/')
            sleep(randint(20,30))

            # invalid shortcode results in a page with a div with 'error-container' class
            error_tags = self.browser.find_elements_by_class_name('error-container')
            if len(error_tags) > 0:
                Log(__ERROR_LOG_FILE__, True, shortcode, 'shortcode not found!')
                return False

            try:
                profile_name = self.browser.find_element_by_xpath('/html/body/span/section/main/div/div/article/header/div[2]/div[1]/div[1]/h2/a').text
                if profile_name in self.__current_profiles__:
                    return False
                if profile_name in self.__black_list__:
                    return False
            except NoSuchElementException:
                profile_name = None
                Log(__ERROR_LOG_FILE__, True, shortcode, 'profile name not found!')

            if like:
                try:
                    like_span = self.browser.find_element_by_xpath('/html/body/span/section/main/div/div/article/div[2]/section[1]/span[1]/button/span')
                    already_liked = 'red' in like_span.get_attribute('class')
                    if not already_liked:
                        like_button = self.browser.find_element_by_xpath('/html/body/span/section/main/div/div/article/div[2]/section[1]/span[1]/button')
                        like_button.click()
                        sleep(3)
                        Log(__ACTION_LOG_FILE__, True, profile_name, shortcode, 'like')
                except NoSuchElementException:
                    Log(__ERROR_LOG_FILE__, True, shortcode, 'like button not found!')

            if follow:
                try:
                    follow_button = self.browser.find_element_by_xpath('/html/body/span/section/main/div/div/article/header/div[2]/div[1]/div[2]/button')
                    if follow_button.text.lower() == 'follow':
                        follow_button.click()
                        sleep(3)
                        Log(__ACTION_LOG_FILE__, True, profile_name, shortcode, 'follow')
                except NoSuchElementException:
                    Log(__ERROR_LOG_FILE__, True, shortcode, 'follow button not found!')

            if comment is not None:
                try:
                    self.browser.find_element_by_xpath('/html/body/span/section/main/div/div/article/div[2]/section[1]/span[2]/button').click()
                    comment_box = self.browser.find_element_by_xpath('/html/body/span/section/main/div/div/article/div[2]/section[3]/div/form/textarea')
                    comment_box.send_keys(comment)
                    comment_box.send_keys(Keys.ENTER)
                    sleep(5)
                    Log(__ACTION_LOG_FILE__, True, profile_name, shortcode, 'comment', comment)
                except NoSuchElementException:
                    Log(__ERROR_LOG_FILE__, True, shortcode, 'comment button or textarea not found!')

            # append processed profile to the list, so its other posts will not be processed.
            self.__current_profiles__.append(profile_name)
            sleep(delay)
        except WebDriverException:
            Log(__ERROR_LOG_FILE__, True, shortcode, 'connection error!')
        return True

    def like_follow_comment_post_2(self, shortcode, like=True, follow=False, comment=None, delay=1):
        if self.browser is None:
            return

        try:
            self.browser.get(__INSTAGRAM_URL__ + 'p/' + shortcode + '/')
            sleep(randint(20,30))

            # invalid shortcode results in a page with a div with 'error-container' class
            error_tags = self.browser.find_elements_by_class_name('error-container')
            if len(error_tags) > 0:
                Log(__ERROR_LOG_FILE__, True, shortcode, 'shortcode not found!')
                return False

            try:
                profile_name = self.browser.find_element_by_xpath('/html/body/span/section/main/div/div/article/header/div[2]/div[1]/div[1]/h2/a').text
                if profile_name in self.__current_profiles__:
                    return False
                if profile_name in self.__black_list__:
                    return False
            except NoSuchElementException:
                profile_name = None
                Log(__ERROR_LOG_FILE__, True, shortcode, 'profile name not found!')

            if like:
                try:
                    like_button = self.browser.find_element_by_xpath('/html/body/span/section/main/div/div/article/div[2]/section[1]/span[1]/button')
                    like_button.click()
                    sleep(3)
                    Log(__ACTION_LOG_FILE__, True, profile_name, shortcode, 'like')
                except NoSuchElementException:
                    Log(__ERROR_LOG_FILE__, True, shortcode, 'like button not found!')

            if follow:
                try:
                    follow_button = self.browser.find_element_by_xpath('/html/body/span/section/main/div/div/article/header/div[2]/div[1]/div[2]/button')
                    if follow_button.text.lower() == 'follow':
                        follow_button.click()
                        sleep(3)
                        Log(__ACTION_LOG_FILE__, True, profile_name, shortcode, 'follow')
                except NoSuchElementException:
                    Log(__ERROR_LOG_FILE__, True, shortcode, 'follow button not found!')

            if comment is not None:
                try:
                    self.browser.find_element_by_xpath('/html/body/span/section/main/div/div/article/div[2]/section[1]/span[2]/button').click()
                    comment_box = self.browser.find_element_by_xpath('/html/body/span/section/main/div/div/article/div[2]/section[3]/div/form/textarea')
                    comment_box.send_keys(comment)
                    comment_box.send_keys(Keys.ENTER)
                    sleep(5)
                    Log(__ACTION_LOG_FILE__, True, profile_name, shortcode, 'comment', comment)
                except NoSuchElementException:
                    Log(__ERROR_LOG_FILE__, True, shortcode, 'comment button or textarea not found!')

            # append processed profile to the list, so its other posts will not be processed.
            self.__current_profiles__.append(profile_name)
            sleep(delay)
        except WebDriverException:
            Log(__ERROR_LOG_FILE__, True, shortcode, 'connection error!')
        return True

    def follow_user(self, user_name, delay=1):
        pass
        return

    def like_follow_comment_hashtag(self, hashtag, like_percent=100, follow_percent=100, comment_percent=100, max_posts=100, delay=1):
        # for each new tag search, __current_profiles__ must be emptied.
        # processed profiles is appended in like_follow_comment_post method.
        self.__current_profiles__ = []

        # hashtag with '#' means that it is for a personal profile and so special random comment with this hashtag must be generated.
        origin_hashtag = hashtag
        hashtag = hashtag.replace('#', '')
        hashtag_result_html = simple_request.simple_get(__INSTAGRAM_HASHTAGS_URL__ + hashtag + '/')
        if hashtag_result_html is None:
            return
        soup = BeautifulSoup(hashtag_result_html, 'html.parser')
        info_script = [str(s) for s in soup.find_all('script') if 'window._sharedData' in str(s) and 'csrf_token' in str(s)]
        if (len(info_script) < 1):
            return
        json_start = info_script[0].find('{')
        json_end = info_script[0].rfind('}')
        if (json_start <= -1 or json_end <= -1):
            return
        result_info = json.loads(info_script[0][json_start:json_end+1])
        try:
            posts = result_info['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['edges']
            counter = 0
            for post in posts:
                shortcode = post['node']['shortcode']
                like = (randint(1, 100) <= like_percent)
                follow = (randint(1, 100) <= follow_percent)
                if post['node']['comments_disabled']:
                    comment = None
                else:
                    comment = InstaBot.get_random_comment(origin_hashtag) if randint(1, 100) <= comment_percent else None
                self.like_follow_comment_post(shortcode=shortcode, like=like, follow=follow, comment=comment, delay=delay)
                # print(shortcode, like, follow, comment)

                counter = counter + 1
                if counter >= max_posts:
                    break
        except KeyError as e:
            print(e)

        # at the end of processing posts of a tag search, __current_profiles__ will be emptied.
        self.__current_profiles__ = []
        return

    def like_profile(self, profile_name, prob=100, max_posts=1):
        if randint(1, 100) <= prob:
            profile_url = 'https://www.instagram.com/' + profile_name
            shortcodes = InstagramTags(profile_url, post_limit=max_posts).get_shortcodes()
            if shortcodes:
                for code in shortcodes:
                    self.like_follow_comment_post(code, like=True, follow=False, comment=None, delay=randint(2, 5))
        return

    def like_hashtag_on_client(self, hashtag, like_percent=100, max_posts=100):
        if self.browser is None:
            return
        self.__current_profiles__ = []
        self.browser.get(__INSTAGRAM_HASHTAGS_URL__ + hashtag + '/')
        sleep(10)
        first_feed = self.browser.find_element_by_xpath('/html/body/span/section/main/article/div[1]/div/div/div[1]/div[1]/a/div/div[2]')
        first_feed.click()
        for i in range(max_posts):
            sleep(randint(10, 20))
            if randint(1, 100) <= like_percent:
                try:
                    profile_name = self.browser.find_element_by_xpath('/html/body/div[3]/div[2]/div/article/header/div[2]/div[1]/div[1]/h2/a').text
                    if profile_name not in self.__current_profiles__ and profile_name not in self.__black_list__:
                        self.__current_profiles__.append(profile_name)
                        try:
                            like_span = self.browser.find_element_by_xpath('/html/body/div[3]/div[2]/div/article/div[2]/section[1]/span[1]/button/span')
                            already_liked = 'red' in like_span.get_attribute('class')
                            if not already_liked:
                                like_button = self.browser.find_element_by_xpath('/html/body/div[3]/div[2]/div/article/div[2]/section[1]/span[1]/button')
                                like_button.click()
                                sleep(randint(5, 8))
                                Log(__ACTION_LOG_FILE__, True, profile_name, '', 'like')
                        except NoSuchElementException:
                            Log(__ERROR_LOG_FILE__, True, profile_name, 'like button not found!')
                except NoSuchElementException:
                    Log(__ERROR_LOG_FILE__, True, '', 'profile name not found!')
            try:
                next_btn = self.browser.find_element_by_xpath('/html/body/div[3]/div[1]/div/div/a[2]')
                next_btn.click()
            except NoSuchElementException:
                try:
                    next_button = self.browser.find_element_by_xpath('/html/body/div[3]/div[1]/div/div/a')
                    next_button.click()
                except NoSuchElementException:
                    Log(__ERROR_LOG_FILE__, True, profile_name, 'next button not found!')
        try:
            close_button = self.browser.find_element_by_xpath('/html/body/div[3]/button[1]')
            close_button.click()
        except NoSuchElementException:
            Log(__ERROR_LOG_FILE__, True, '', 'close button not found!')
        return

    @staticmethod
    def get_random_comment(hashtag=None):
        if hashtag is None or hashtag[0] != '#':
            # comments = ['چه مطلب جالبی 🌹', 'بسیار عالی 🌹', 'خیلی خوبه 🌹', 'حرف نداره 🌹']
            # comments = ['برای مشاهده نمایش گرافیکی جذاب از واژه‌های داغ خبری، ورزشی و سینمایی تگ نشان را فالو کنید. 🌹', 'با تگ نشان واژه‌ها و هشتگهای پرکاربرد خود را بشناسید. 🌹']
            comments = [ \
                'با تگ نشان از روزها و ساعتهایی که پستهای شما بیشترین لایک و کامنت را گرفته‌اند آگاه شوید. 🌹', \
                'با تگ نشان از تعداد لایک و کامنتی که هشتگ‌ها گرفته‌اند آگاه شوید. 🌹', \
                'با تگ نشان واژه‌ها و هشتگهای پرکاربرد خود را بشناسید. 🌹']
            index = randint(0, len(comments)-1)
            comment = comments[index]
        else:
            # comment = '{} بیشتر چه واژه‌ها و هشتگ‌هایی را در صفحه اینستاگرامش به کار برده؟ برای مشاهده به تگ نشان سر بزنید 🌹🌹'.format(hashtag[1:])
            comment = '{} در صدر صفحه‌های سینمایی در اینستاگرام. برای مشاهده هشتگ‌های داغ شده به تگ نشان سر بزنید 🌹🌹'.format(hashtag[1:])
            # comment = 'به امید روزی که دیگه دچار سیل و زلزله و سایر بلایای طبیعی نشیم.'
        return comment

############################################################################################

# def insta_tags_action(insta_bot, tag_file, user_name, user_password):
def insta_tags_action(insta_bot, tag_file):
    """
    1. reads first tag from tag_file.
    2. creates bot for profile with user_name and password.
    3. searches posts with hashtag and then likes, follows and puts comment on them
    4. moves tag to end of tag_file.
    """
    with open(tag_file) as f:
        tag_str = f.read()
    tags = tag_str.split('\n')
    top_tag = tags[0]
    
    # bot = InstaBot()
    # if bot.login(user_name, user_password, delay=randint(5, 10)):
    #     bot.like_follow_comment_hashtag(hashtag=top_tag, like_percent=100, follow_percent=0, comment_percent=0, max_posts=100, delay=randint(5, 10))
    # else:
    #     print('Login Failed!')

    # insta_bot.like_follow_comment_hashtag(hashtag=top_tag, like_percent=100, follow_percent=0, comment_percent=0, max_posts=100, delay=randint(1, 3))
    bot.like_hashtag_on_client(top_tag, like_percent=70, max_posts=100)

    tags.remove(top_tag)
    tags.append(top_tag)
    with open(tag_file, 'w') as f:
        f.write('\n'.join(tags))
    return

def insta_profiles_action(insta_bot, profiles_file, prob=100):
    """
    1. reads profile names from profile_file.
    2. likes recently post of each profile with probability prob
    """
    with open(profiles_file) as f:
        profiles_str = f.read()
    profiles = profiles_str.split('\n')
    
    for profile_name in profiles:
        insta_bot.like_profile(profile_name, prob=prob, max_posts=1)
    return

############################################################################################
if __name__ == "__main__":
    # bot = InstaBot()
    # if bot.login('tahchinbot', 'volcano112', delay=randint(5, 10)):
    #     bot.like_hashtag_on_client('همبرگر', like_percent=50, max_posts=10)
    # exit(0)
    pass
    # insta_tags_action('./instadata/bottags.txt', 'tagneshan.ir', 'volcano112')

    hashtag_count = int(input('Enter hashtag count: '))

    bot = InstaBot()
    if bot.login('axneshan', 'volcano112', delay=randint(8, 12)):
        for i in range(0, hashtag_count):
            print(i+1, '...')
            insta_tags_action(bot, './instadata/bottags.txt')
            print('Waiting ...')
            sleep(randint(120, 180))
        print('Finished!')
        # bot.__current_profiles__ = []
        # insta_profiles_action(bot, './instadata/_following.txt', prob=15)
        # insta_profiles_action(bot, './instadata/_followers.txt', prob=10)
        # insta_profiles_action(bot, './instadata/_top_profiles.txt', prob=80)
    else:
        print('Login Failed!')

    # r = bot.login('rooznema.ir', 'wonder112land', delay=randint(5, 10))
    # bot.like_profile('tahchinbot', prob=100, max_posts=4)
    # bot.like_follow_comment_hashtag(hashtag='آشپزی', like_percent=100, follow_percent=10, comment_percent=30, max_posts=5, delay=randint(5, 10))
    # r = bot.like_follow_comment_post('BX2V4ZZgdgm', like=True, follow=False, comment=None, delay=randint(5, 10))
    # r = bot.like_follow_comment_post('BYFsfZCglRx', like=True, follow=False, comment=None, delay=randint(5, 10))
    # print(r)
