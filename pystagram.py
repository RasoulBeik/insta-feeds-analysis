import os
import re
import json
import time
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from random import randint
from collections import OrderedDict
from selenium import webdriver
from bs4 import BeautifulSoup
from PIL import Image, ImageFont
from datetime import datetime
from six import text_type
from persiantext import PersianText
from wordcloud_generator import WCGenerator
from snowyimage import SnowyImage
from text2image import Text2Image
import cartoonizer
import simple_request

# __BASE_PATH__ = '/home/emroozfe/public_html/insta'
__BASE_PATH__ = '.'
__CONTENT_PATH__ = 'instadata'
__IMAGE_PATH__ = 'images'
__OUTPUT_PATH__ = 'outputs'
__FONT_PATH__ = 'fonts'
__FONT_ZIBA__ = os.path.join(__BASE_PATH__, __FONT_PATH__, 'Arghavan.ttf') #'AdobeArabic-Bold.otf')
__FONT__ = os.path.join(__BASE_PATH__, __FONT_PATH__, 'AdobeArabic-Bold.otf')
__EXT_SHORTCODE__ = '.shortcode'
__EXT_HASHTAG__ = '.hashtag'
__EXT_CAPTION__ = '.caption'
__EXT_JPG__ = '.jpg'
__EXT_PNG__ = '.png'
__EXT_CSV__ = '.csv'
__EXT_JSON__ = '.json'
__EXT_TEMP__ = '.tmp'
__SEPARATOR__ = '***^^^***'
__INSTAGRAM_URL__ = 'https://www.instagram.com/'
__INSTAGRAM_TAGS_URL__ = 'https://www.instagram.com/explore/tags/'
__PROFILES_FILE__ = 'profiles.txt'
__SIGN_INFO__ = {'text': '@tagneshan.ir', 'location': 'bottom left', 'color': 'red', 'font': ImageFont.truetype('arial.ttf', size=40)}
__WORD_LABEL__ = {'text': '*** واژه‌های پرکاربرد ***', 'location': 'bottom center', 'color': 'red', 'font': ImageFont.truetype(__FONT_ZIBA__, size=40)}
__HASHTAG_LABEL__ = {'text': '*** هشتگ‌های پرکاربرد ***', 'location': 'bottom center', 'color': 'red', 'font': ImageFont.truetype(__FONT_ZIBA__, size=40)}
__PERSIAN_DAYS__ = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه']
__ENGLISH_DAYS = ['Moday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

__STOPWORDS1__ = ['']

class InstaProfile:
    def __init__(self, profile_name):
        self.__profile_name__ = profile_name
        self.__info_json__ = None
        self.__shortcodes__ = []
        return

    def hashtags_filename(self):
        return os.path.join(__BASE_PATH__, __CONTENT_PATH__, self.__profile_name__+__EXT_HASHTAG__)

    def captions_filename(self):
        return os.path.join(__BASE_PATH__, __CONTENT_PATH__, self.__profile_name__+__EXT_CAPTION__)
        
    def base_info_filename(self):
        return os.path.join(__BASE_PATH__, __CONTENT_PATH__, self.__profile_name__+__EXT_JSON__)
        
    def get_base_info(self, with_feedback=True):
        if with_feedback:
            print('>>', self.__class__.__name__, 'get_base_info')
        try:
            profile_url = os.path.join(__INSTAGRAM_URL__, self.__profile_name__)
            profile_html = simple_request.simple_get(profile_url)
            if profile_html is None:
                return
            soup = BeautifulSoup(profile_html, 'html.parser')
            info_script = [str(s) for s in soup.find_all('script') if 'window._sharedData' in str(s) and 'csrf_token' in str(s)]
            if (len(info_script) < 1):
                return
            json_start = info_script[0].find('{')
            json_end = info_script[0].rfind('}')
            if (json_start == -1 or json_end == -1):
                return
            self.__info_json__ = json.loads(info_script[0][json_start:json_end+1])
            if self.__info_json__:
                with open(self.base_info_filename(), 'w') as f:
                    json.dump(self.__info_json__, f, ensure_ascii=False)
            time.sleep(randint(1, 3))
        except TypeError:
            self.__info_json__ = None
        return

    def get_followers_following(self):
        if not self.__info_json__:
            return 0, 0

        followers, following = 0, 0
        try:
            followers = self.__info_json__['entry_data']['ProfilePage'][0]['graphql']['user']['edge_followed_by']['count']
            following = self.__info_json__['entry_data']['ProfilePage'][0]['graphql']['user']['edge_follow']['count']
        except KeyError:
            followers, following = 0, 0
        return followers, following

    def get_posts_count(self):
        if not self.__info_json__:
            return 0

        posts = 0
        try:
            posts = self.__info_json__['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['count']
        except KeyError:
            posts = 0
        return posts

    def get_posts_shorcodes(self, scroll_limit=None, with_feedback=True):
        if with_feedback:
            print('>>', self.__class__.__name__, 'get_posts_shortcodes')

        # 1 scroll_limit = 12 posts
        # scroll_limit = None: all posts

        # I used Firefox; you can use whichever browser you like.
        # browser = webdriver.Firefox()
        browser = webdriver.Firefox(firefox_binary = '/opt/firefox-dev/firefox')

        extension_path = '/home/rasoul/.mozilla/firefox/m03saqxc.default/extensions/@hoxx-vpn.xpi'  # Must be the full path to an XPI file!
        browser.install_addon(extension_path, temporary=True)
        input('***** Setup proxy if needed and then press ENTER ...')

        # Tell Selenium to get the URL you're interested in.
        profile_url = os.path.join(__INSTAGRAM_URL__, self.__profile_name__)
        browser.get(profile_url)

        # Selenium script to scroll to the bottom, wait 5 seconds for the next batch of data to load, then continue scrolling.
        # It will continue to do this until the page stops loading new data.
        len_of_page = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match = False
        limit = 0
        while not match:
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            span = soup.find('span', id='react-root')
            if span:
                links = span.find_all('a', href=re.compile('/p/'))
                if links:
                    self.__shortcodes__ = self.__shortcodes__ + [l['href'] for l in links]
            last_count = len_of_page
            time.sleep(10)
            len_of_page = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            if last_count == len_of_page:
                match = True

            # scroll_limit is used to prevent scrolling to the end of page.
            # if it is None, it means scroll to the end of page.
            limit = limit + 1
            if scroll_limit is not None:
                if limit >= scroll_limit:
                    break

        self.__shortcodes__ = set(self.__shortcodes__)
        self.__shortcodes__ = [shortcode.replace('/p/', '').replace('/', '') for shortcode in self.__shortcodes__]
        return

    def read_base_info(self):
        if not os.path.exists(self.base_info_filename()):
            self.__info_json__ = None
        else:
            with open(self.base_info_filename(), 'r') as f:
                self.__info_json__ = json.load(f)
        return

    def read_posts_shortcodes(self, append=True):
        file_name = self.__profile_name__ + __EXT_SHORTCODE__
        file_path = os.path.join(__BASE_PATH__, __CONTENT_PATH__, file_name)
        if not os.path.exists(file_path):
            return
        with open(file_path, 'r') as f:
            shortcode_str = f.read()
            if append:
                temp = set(self.__shortcodes__ + shortcode_str.split(' '))
                self.__shortcodes__ = list(temp)
            else:
                self.__shortcodes__ = shortcode_str.split()
        return

    def save_posts_shortcodes(self):
        # self.read_posts_shortcodes(append=False)
        file_name = self.__profile_name__ + __EXT_SHORTCODE__
        file_path = os.path.join(__BASE_PATH__, __CONTENT_PATH__, file_name)
        with open(file_path, 'w') as f:
            f.write(' '.join(self.__shortcodes__))
        return

    def save_posts_info(self, append=True, with_feedback=True):
        """
        append = True: appends new info to the file
        append = False: overwrites file if exists
        """
        if with_feedback:
            print('>>', self.__class__.__name__, 'save_posts_info')

        if not self.__shortcodes__:
            return False
        hashtags = []
        captions = []
        infos = []
        for shortcode in self.__shortcodes__:
            post = InstaPost(self.__profile_name__, shortcode)
            if post.__hashtags__ is not None:
                hashtags = hashtags + post.__hashtags__
            post_caption = post.get_caption()
            if post_caption is not None:
                captions.append(post_caption)
            post_like_counts = post.get_like_counts()
            post_like_counts = 0 if post_like_counts is None else post_like_counts
            post_comment_counts = post.get_comment_counts()
            post_comment_counts = 0 if post_comment_counts is None else post_comment_counts
            post_ts = post.get_timestamp()
            ht = '' if post.__hashtags__ is None else ' '.join(post.__hashtags__)
            infos.append('{},{},{},{},{}'.format(shortcode, ht, post_like_counts, post_comment_counts, post_ts))
            time.sleep(randint(1, 3))
        try:
            mode = 'a' if append else 'w'
            if len(hashtags) > 0:
                fn = self.__profile_name__ + __EXT_HASHTAG__
                with open(os.path.join(__BASE_PATH__, __CONTENT_PATH__, fn), mode) as f:
                    f.write(' '.join(hashtags))
            if len(captions) > 0:
                fn = self.__profile_name__ + __EXT_CAPTION__
                with open(os.path.join(__BASE_PATH__, __CONTENT_PATH__, fn), mode) as f:
                    f.write(__SEPARATOR__.join(captions))
            if len(infos) > 0:
                fn = self.__profile_name__ + __EXT_CSV__
                with open(os.path.join(__BASE_PATH__, __CONTENT_PATH__, fn), mode) as f:
                    if mode == 'w':
                        f.write('shortcode,hashtags,likes,comments,timestamp\n')
                    f.write('\n'.join(infos))
            return True
        except IOError as e:
            print(e)
            return False

    def get_all_hashtags(self):
        if not self.__shortcodes__:
            return None
        hashtags = []
        for shortcode in self.__shortcodes__:
            if InstaPost(self.__profile_name__, shortcode).__hashtags__ is not None:
                hashtags = hashtags + InstaPost(self.__profile_name__, shortcode).__hashtags__
        if len(hashtags) == 0:
            return None
        return hashtags

    def get_persian_hashtags(self):
        tags = self.get_all_hashtags()
        if tags is None:
            return None
        tags = [t for t in tags if re.search('[a-zA-Z]', t) is None]   # removes tags with english letters
        if len(tags) == 0:
            return None
        return tags

    def get_engagement_rate(self, first_idx, last_idx):
        csv_file = os.path.join(__BASE_PATH__, __CONTENT_PATH__, self.__profile_name__+__EXT_CSV__)
        if not os.path.exists(csv_file):
            print(csv_file, 'not found!')
            return None
        df = pd.read_csv(csv_file)
        df_sorted = df.sort_values(by='timestamp', axis=0, ascending=False)
        likes = df_sorted[first_idx:last_idx]['likes'].sum()
        comments = df_sorted[first_idx:last_idx]['comments'].sum()
        followers, _ = self.get_followers_following()
        if followers == 0:
            return None
        else:
            return round(((likes + comments) / (last_idx - first_idx)) / followers * 100, 1)

    def generate_image_file_name(self, info_type=''):
        """
        generates a file name for image.
        format: [profile name].[info type].[current date].[extension]
        info_type: caption or hashtag
        """
        ts = datetime.now().timestamp()
        t = datetime.fromtimestamp(ts)
        date_str = t.strftime('%Y%m%d')
        return '{}{}.{}{}'.format(self.__profile_name__, info_type, date_str, __EXT_PNG__)

    def generate_caption_wordcloud(self, font_path=None, mask=None, background_color='black', repeat=False, scale=1,
                                   colormap=None, contour_width=0, contour_color='black', color_func=None):
        input_file = os.path.join(__BASE_PATH__, __CONTENT_PATH__, self.__profile_name__+__EXT_CAPTION__)
        if not os.path.exists(input_file):
            print('{} not found!'.format(input_file))
            return
        
        text = ''
        with open(input_file, 'r') as f:
            text = f.read()

        stop_words = [['نمی', 'هایی', 'های', 'اند', 'کردن', 'ترین', 'مان', 'هایش']]

        output_file = os.path.join(__BASE_PATH__, __OUTPUT_PATH__, self.generate_image_file_name(__EXT_CAPTION__))
        pt = PersianText(text) \
            .replace([('\n', ' '), (__SEPARATOR__, ' '), ('_', '-'), ('ك', 'ک'), ('ي', 'ی')]) \
            .tokenize() \
            .filter_tokens(pos_tags=['N'], language='fa', min_len=3, reshape=True, stop_words=stop_words)
        pt.generate_wordcloud(font_path=font_path, mask=mask, background_color=background_color,
                              scale=scale, colormap=colormap,
                              display_online=False, output_file=output_file,
                              output_file_sign=__SIGN_INFO__, output_file_text=__WORD_LABEL__)
        print('Word cloud generated in {}'.format(output_file))
        return

    def generate_hashtag_wordcloud(self, font_path=None, mask=None, background_color='black', repeat=False, scale=1,
                                   colormap=None, contour_width=0, contour_color='black', color_func=None):
        input_file = os.path.join(__BASE_PATH__, __CONTENT_PATH__, self.__profile_name__+__EXT_HASHTAG__)
        if not os.path.exists(input_file):
            print('{} not found!'.format(input_file))
            return
        
        text = ''
        with open(input_file, 'r') as f:
            text = f.read()

        output_file = os.path.join(__BASE_PATH__, __OUTPUT_PATH__, self.generate_image_file_name(__EXT_HASHTAG__))
        pt = PersianText(text).replace([('_', '-'), ('ك', 'ک'), ('ي', 'ی')]) \
                              .tokenize().filter_tokens(language='fa', min_len=1, reshape=True)
        pt.generate_wordcloud(font_path=font_path, mask=mask, background_color=background_color,
                              scale=scale, colormap=colormap,
                              display_online=False, output_file=output_file,
                              output_file_sign=__SIGN_INFO__, output_file_text=__HASHTAG_LABEL__)
        print('Word cloud generated in {}'.format(output_file))
        return

    def generate_snowy_photo(self, shortcode, photo_enhance_factor=3, photo_exists=True):
        if not photo_exists:
            InstaPost(self.__profile_name__, shortcode).get_photo(os.path.join(__BASE_PATH__, __IMAGE_PATH__))

        file_name = '{}-{}{}'.format(self.__profile_name__, shortcode, __EXT_JPG__)
        input_file = os.path.join(__BASE_PATH__, __IMAGE_PATH__, file_name)
        try:
            output_file = os.path.join(__BASE_PATH__, __OUTPUT_PATH__, file_name)
            WCGenerator.generate_colored_image(input_file, output_file, input_enhance_factor=photo_enhance_factor, output_enhance_factor=1, max_words=500000)
            WCGenerator.enhance_image(output_file, enhance_factor=2)
            WCGenerator.enhance_image(output_file, enhance_factor=3)
        except IOError as e:
            print(e)
        return

    def generate_day_hour_heatmaps(self, width_inch=15, height_inch=5, likes_save_to=None, comments_save_to=None):
        csv_file = os.path.join(__BASE_PATH__, __CONTENT_PATH__, self.__profile_name__+__EXT_CSV__)
        if not os.path.exists(csv_file):
            print(csv_file, 'not found!')
            return
        sum_cols = ['likes', 'comments']
        df = pd.read_csv(csv_file)
        df['post_day'] = df['timestamp'].apply(lambda x: pd.Timestamp(int(x), unit='s', tz='Asia/Tehran').dayofweek)
        df['post_hour'] = df['timestamp'].apply(lambda x: pd.Timestamp(x, unit='s', tz='Asia/Tehran').hour)
        df_aggregate = df.groupby(by=['post_day', 'post_hour']).sum()[sum_cols] / df.groupby(by=['post_day', 'post_hour']).count()[sum_cols]

        df_temp = df_aggregate['likes'].unstack()
        df_temp = df_temp.reindex(range(7))
        df_temp = df_temp.T.reindex(range(24)).T.fillna(0)
        df_temp = pd.DataFrame(df_temp.values, index=[2, 3, 4, 5, 6, 0, 1]).reindex(range(7))
        df_temp.index = [PersianText.reshape(pd) for pd in __PERSIAN_DAYS__]
        plt.figure(figsize=(width_inch, height_inch))
        ax = plt.gca()
        plt.title(PersianText.reshape('متوسط تعداد لایک بر حسب روز و ساعت ارسال پست'))
        sns.heatmap(df_temp, linewidths=0.5, cmap='Reds')
        plt.yticks(rotation=45)
        if likes_save_to is not None:
            plt.savefig(likes_save_to)
        plt.close()

        df_temp = df_aggregate['comments'].unstack()
        df_temp = df_temp.reindex(range(7))
        df_temp = df_temp.T.reindex(range(24)).T.fillna(0)
        df_temp = pd.DataFrame(df_temp.values, index=[2, 3, 4, 5, 6, 0, 1]).reindex(range(7))
        df_temp.index = [PersianText.reshape(pd) for pd in __PERSIAN_DAYS__]
        plt.figure(figsize=(width_inch, height_inch))
        ax = plt.gca()
        plt.title(PersianText.reshape('متوسط تعداد کامنت بر حسب روز و ساعت ارسال پست'))
        sns.heatmap(df_temp, linewidths=0.5, cmap='Greens')
        plt.yticks(rotation=45)
        if comments_save_to is not None:
            plt.savefig(comments_save_to)
        plt.close()
        return

    def generate_day_aggregate_charts(self, **kwargs):
        csv_file = os.path.join(__BASE_PATH__, __CONTENT_PATH__, self.__profile_name__+__EXT_CSV__)
        if not os.path.exists(csv_file):
            print(csv_file, 'not found!')
            return
        sum_cols = ['likes', 'comments']
        df = pd.read_csv(csv_file)
        df['post_day'] = df['timestamp'].apply(lambda x: pd.Timestamp(int(x), unit='s', tz='Asia/Tehran').dayofweek)

        df_day_aggregate = df.groupby(by='post_day').sum()[sum_cols] / df.groupby(by='post_day').count()[sum_cols]
        # a one column dataframe contains range(0,7) values.
        # this dataframe is joined on left with df_day_aggregate to fill missed days.
        df_sequence = pd.DataFrame({'i':[i for i in range(0, 7)]})
        df_day_aggregate = pd.merge(df_sequence, df_day_aggregate, how='left', left_on='i', right_on='post_day').fillna(0)[sum_cols]
        # index is post_day and it starts from 0 as monday. it must be shifted to convert saturday as 0
        df_day_aggregate.index = (df_day_aggregate.index + 2) % 7
        # df_day_aggregate.reset_index(inplace=True, drop=True)
        df_day_aggregate.sort_index(inplace=True)
        kwargs['title'] = 'متوسط تعداد لایک‌ها و کامنت‌ها در روزهای ارسال پست'
        kwargs['xlabel'] = 'روز'
        kwargs['ylabel'] = 'تعداد'
        kwargs['legend_labels'] = ['لایک', 'کامنت']
        kwargs['xticks'] =__PERSIAN_DAYS__
        self.__generate_bar__(df_day_aggregate, **kwargs)
        return

    def generate_hour_aggregate_charts(self, **kwargs):
        csv_file = os.path.join(__BASE_PATH__, __CONTENT_PATH__, self.__profile_name__+__EXT_CSV__)
        if not os.path.exists(csv_file):
            print(csv_file, 'not found!')
            return
        sum_cols = ['likes', 'comments']
        df = pd.read_csv(csv_file)
        df['post_hour'] = df['timestamp'].apply(lambda x: pd.Timestamp(x, unit='s', tz='Asia/Tehran').hour)

        df_hour_aggregate = df.groupby(by='post_hour').sum()[sum_cols] / df.groupby(by='post_hour').count()[sum_cols]
        # a one column dataframe contains range(0,24) values.
        # this dataframe is joined on left with df_hour_aggregate to fill missed hours.
        df_sequence = pd.DataFrame({'i':[i for i in range(0, 24)]})
        df_hour_aggregate = pd.merge(df_sequence, df_hour_aggregate, how='left', left_on='i', right_on='post_hour').fillna(0)[sum_cols]
        kwargs['title'] = 'متوسط تعداد لایک‌ها و کامنت‌ها در ساعتهای ارسال پست'
        kwargs['xlabel'] ='ساعت'
        kwargs['ylabel'] ='تعداد'
        kwargs['legend_labels'] =['لایک', 'کامنت']
        self.__generate_bar__(df_hour_aggregate, **kwargs)
        return

    def generate_hashtags_charts(self, sum_col, max_hashtags=None, **kwargs):
        csv_file = os.path.join(__BASE_PATH__, __CONTENT_PATH__, self.__profile_name__+__EXT_CSV__)
        if not os.path.exists(csv_file):
            print(csv_file, 'not found!')
            return
        df = pd.read_csv(csv_file)
        df = df.dropna(axis=0)
        hashtags_set = set((' '.join(df['hashtags'].values)).split())
        sum_results = []
        for ht in hashtags_set:
            s = 0
            ht_count = 0
            for _, row in df.iterrows():
                if ht in row['hashtags']:
                    s = s + row[sum_col]
                    ht_count = ht_count + 1
            if ht_count > 0:
                sum_results.append(s/ht_count)
            else:
                sum_results.append(0)

        reshaped_hashtags = [PersianText.reshape(ht) for ht in hashtags_set]

        df_col_hashtags = pd.DataFrame({'sum_col':sum_results}, index=reshaped_hashtags)
        df_col_hashtags.sort_values(by='sum_col', inplace=True, ascending=False)
        self.__generate_bar__(df_col_hashtags.head(max_hashtags), **kwargs)
        return

    def __generate_bar__(self, dataframe, **kwargs):
        """
        **kwargs:
            title: title of image
            width_inch, height_inch: width and height of the result image in inch
            font_name: font path and name of texts on image
            xlabel, ylabel: labels of x and y axis
            xticks: list of strings that should be shown on x axis
            legend_labels: labels of legend
        """
        title = None
        if 'title' in kwargs:
            title = PersianText.reshape(kwargs['title'])
            del kwargs['title']
        xlabel = None
        if 'xlabel' in kwargs:
            xlabel = PersianText.reshape(kwargs['xlabel'])
            del kwargs['xlabel']
        ylabel = None
        if 'ylabel' in kwargs:
            ylabel = PersianText.reshape(kwargs['ylabel'])
            del kwargs['ylabel']
        legend_labels = None
        if 'legend_labels' in kwargs:
            legend_labels = [PersianText.reshape(l) for l in kwargs['legend_labels']]
            del kwargs['legend_labels']
        width_inch = 16
        if 'width_inch' in kwargs:
            width_inch = kwargs['width_inch']
            del kwargs['width_inch']
        height_inch = 16
        if 'height_inch' in kwargs:
            height_inch = kwargs['height_inch']
            del kwargs['height_inch']
        font_name = None
        if 'font_name' in kwargs:
            font_name = kwargs['font_name']
            del kwargs['font_name']
        xticks = None
        if 'xticks' in kwargs:
            xticks = [PersianText.reshape(xt) for xt in kwargs['xticks']]
            del kwargs['xticks']
        save_to = None
        if 'save_to' in kwargs:
            save_to = kwargs['save_to']
            del kwargs['save_to']

        font = fm.FontProperties(fname=font_name, size=1.5*width_inch)

        plt.figure(figsize=(width_inch, height_inch))
        ax = plt.gca()
        # plt.bar(range(len(samples)), freqs, **kwargs)
        dataframe.plot.bar(ax=ax, **kwargs)
        if xticks is not None:
            plt.xticks(range(len(xticks)), [text_type(xt) for xt in xticks], rotation=45, fontproperties=font, horizontalalignment='right')
        else:
            plt.xticks(rotation=45, fontproperties=font, horizontalalignment='right')
        plt.yticks(fontproperties=font)
        font.set_size(2.5*width_inch)
        plt.title(title, fontproperties=font)
        plt.xlabel(xlabel, fontproperties=font)
        plt.ylabel(ylabel, fontproperties=font)
        if legend_labels is not None:
            font.set_size(15)
            plt.legend(legend_labels, prop=font)
        plt.tight_layout()
        if save_to is not None:
            plt.savefig(save_to)
        else:
            plt.show()
        plt.close()
        return

    def generate_summary_report(self, **kwargs):
        csv_file = os.path.join(__BASE_PATH__, __CONTENT_PATH__, self.__profile_name__+__EXT_CSV__)
        if not os.path.exists(csv_file):
            print(csv_file, 'not found!')
            return
        df = pd.read_csv(csv_file)
        primary_len = len(df)
        # df = df.dropna(axis=0)
        df['hashtags'].fillna('', inplace=True)
        df['hashtag_count'] = df['hashtags'].apply(lambda x: len(x.split()))
        df['post_day'] = df['timestamp'].apply(lambda x: pd.Timestamp(x, unit='s', tz='Asia/Tehran').dayofweek)
        df['post_hour'] = df['timestamp'].apply(lambda x: pd.Timestamp(x, unit='s', tz='Asia/Tehran').hour)

        # min and max of likes and comments for each hashtag
        # hashtags with min and max likes and comments
        hashtag_likes = {}
        hashtag_comments = {}
        hashtags_set = set((' '.join(df['hashtags'].values)).split())
        for ht in hashtags_set:
            likes = 0
            comments = 0
            ht_count = 0
            for _, row in df.iterrows():
                if ht in row['hashtags']:
                    likes = likes + row['likes']
                    comments = comments + row['comments']
                    ht_count = ht_count + 1
            hashtag_likes[ht] = likes / ht_count if ht_count > 0 else 0
            hashtag_comments[ht] = comments / ht_count if ht_count > 0 else 0
        max_likes = max(hashtag_likes.values())
        max_likes_hashtags = [key for key in hashtag_likes if hashtag_likes[key] == max_likes]
        max_comments = max(hashtag_comments.values())
        max_comments_hashtags = [key for key in hashtag_comments if hashtag_comments[key] == max_comments]
        min_likes = min(hashtag_likes.values())
        min_likes_hashtags = [key for key in hashtag_likes if hashtag_likes[key] == min_likes]
        min_comments = min(hashtag_comments.values())
        min_comments_hashtags = [key for key in hashtag_comments if hashtag_comments[key] == min_comments]

        # the hours with max likes and hashtags
        df_hour_aggregate = df.groupby(by='post_hour').sum()[['likes', 'comments']] / df.groupby(by='post_hour').count()
        m = df_hour_aggregate['likes'].max()
        max_likes_hours = list(df_hour_aggregate[df_hour_aggregate['likes'] == m].index.values)
        max_likes_hours = [str(h) for h in max_likes_hours]
        m = df_hour_aggregate['comments'].max()
        max_comments_hours = list(df_hour_aggregate[df_hour_aggregate['comments'] == m].index.values)
        max_comments_hours = [str(h) for h in max_comments_hours]

        # the days with max likes and hashtags
        df_day_aggregate = df.groupby(by='post_day').sum()[['likes', 'comments']] / df.groupby(by='post_day').count()
        m = df_day_aggregate['likes'].max()
        max_likes_days = [__PERSIAN_DAYS__[(i+2)%7] for i in df_day_aggregate[df_day_aggregate['likes'] == m].index.values]
        m = df_day_aggregate['comments'].max()
        max_comments_days = [__PERSIAN_DAYS__[(i+2)%7] for i in df_day_aggregate[df_day_aggregate['comments'] == m].index.values]

        eng_rate_10 = self.get_engagement_rate(0, 10)
        eng_rate_30 = self.get_engagement_rate(0, 30)

        summary = {}
        summary['post_count'] = primary_len
        summary['hashtags_mean'] = int(round(df['hashtag_count'].mean()))
        summary['likes_mean'] = int(round(df['likes'].mean()))
        summary['comments_mean'] = int(round(df['comments'].mean()))
        summary['max_likes'] = max_likes
        summary['max_likes_hashtags'] = max_likes_hashtags if max_likes != 0 else '-'
        summary['max_comments'] = max_comments
        summary['max_comments_hashtags'] = max_comments_hashtags if max_comments != 0 else '-'
        summary['min_likes'] = min_likes
        summary['min_likes_hashtags'] = min_likes_hashtags if min_likes != 0 else '-'
        summary['min_comments'] = min_comments
        summary['min_comments_hashtags'] = min_comments_hashtags if min_comments != 0 else '-'
        summary['max_likes_hours'] = max_likes_hours if max_likes != 0 else '-'
        summary['max_comments_hours'] = max_comments_hours if max_comments != 0 else '-'
        summary['max_likes_days'] = max_likes_days if max_likes != 0 else '-'
        summary['max_comments_days'] = max_comments_days if max_comments != 0 else '-'
        summary['eng_rate_10'] = eng_rate_10 if eng_rate_10 is not None else 'نامعلوم'
        summary['eng_rate_30'] = eng_rate_30 if eng_rate_30 is not None else 'نامعلوم'

        is_demo = True
        if 'is_demo' in kwargs:
            is_demo = kwargs['is_demo']
        if is_demo:
            image_size = (1200, 1400)
            followers, _ = self.get_followers_following()
            if followers < 1000:
                followers_str = str(followers)
            else:
                followers_str = str(followers//100/10) + 'k'

            eng_rate_10 = eng_rate_10 if eng_rate_10 is not None else 0
            if eng_rate_10 < 4:
                msg1 = 'مخاطبان تعامل ضعیفی با صفحه شما دارند و'
                msg2 = 'تعداد لایک و کامنت پست‌ها کم است!'
                msg_color = 'darkred'
            elif eng_rate_10 < 8:
                msg1 = 'مخاطبان تعامل مناسبی با صفحه شما دارند و'
                msg2 = 'تعداد لایک و کامنت پست‌ها متوسط است.'
                msg_color = 'darkorange'
            else:
                msg1 = 'مخاطبان تعامل خوبی با صفحه شما دارند و'
                msg2 = 'تعداد لایک و کامنت پست‌ها زیاد است.'
                msg_color = 'darkgreen'

            report_template_file = os.path.join(__BASE_PATH__, __CONTENT_PATH__, '__profile-report-template.demo.2.txt')
            with open(report_template_file) as f:
                template_text = f.read()
            report_text = template_text.format(
                                            self.__profile_name__,
                                            summary['post_count'],
                                            followers_str, msg_color, msg1, msg_color, msg2, msg_color, eng_rate_10
                                            # summary['eng_rate_10'],
                                            # summary['hashtags_mean'],
                                            # summary['likes_mean'], summary['max_likes'],
                                            # ' '.join(summary['max_likes_hashtags']),
                                            # ' '.join(summary['max_likes_days']),
                                            # ' '.join(summary['max_likes_hours']),
                                            # summary['comments_mean'], summary['max_comments'],
                                            # ' '.join(summary['max_comments_hashtags']),
                                            # ' '.join(summary['max_comments_days']),
                                            # ' '.join(summary['max_comments_hours'])
                                            )
        else:
            image_size = (1000, 1520)
            report_template_file = os.path.join(__BASE_PATH__, __CONTENT_PATH__, '__profile-report-template.main.txt')
            with open(report_template_file) as f:
                template_text = f.read()
            report_text = template_text.format(
                                            self.__profile_name__,
                                            summary['post_count'],
                                            summary['eng_rate_10'],
                                            summary['eng_rate_30'],
                                            summary['hashtags_mean'],
                                            summary['likes_mean'], summary['max_likes'],
                                            ' '.join(summary['max_likes_hashtags']),
                                            ' '.join(summary['max_likes_days']),
                                            ' '.join(summary['max_likes_hours']),
                                            summary['comments_mean'], summary['max_comments'],
                                            ' '.join(summary['max_comments_hashtags']),
                                            ' '.join(summary['max_comments_days']),
                                            ' '.join(summary['max_comments_hours'])
                                            )
        if 'save_to' in kwargs:
            Text2Image(report_text, image_size=image_size, margin=30, line_space=15, background_color='white').save(kwargs['save_to'])
        return

    # def get...(self, item):
    #     pass

# ##################################################################################

class InstaPost:
    def __init__(self, profile_name, post_shortcode, with_feedback=True):
        if with_feedback:
            print('>>', self.__class__.__name__, '__init__', post_shortcode)

        self.__profile_name__ = profile_name
        self.__shortcode__ = post_shortcode
        self.__info_json__ = None
        self.__hashtags__ = None

        post_url = os.path.join(__INSTAGRAM_URL__, 'p', post_shortcode)
        post_html = simple_request.simple_get(post_url)
        if post_html is None:
            return
        soup = BeautifulSoup(post_html, 'html.parser')

        # extract json info
        info_script = [str(s) for s in soup.find_all('script') if 'window._sharedData' in str(s) and 'csrf_token' in str(s)]
        if (len(info_script) < 1):
            return
        json_start = info_script[0].find('{')
        json_end = info_script[0].rfind('}')
        if (json_start <= -1 or json_end <= -1):
            return
        self.__info_json__ = json.loads(info_script[0][json_start:json_end+1])

        # extract hashtags
        hashtags = [meta['content'] for meta in soup.find_all('meta', property='instapp:hashtags')]
        video_hashtags = [meta['content'] for meta in soup.find_all('meta', property='video:tag')]
        if hashtags and video_hashtags:
            self.__hashtags__ = hashtags + video_hashtags
        elif hashtags:
            self.__hashtags__ = hashtags
        elif video_hashtags:
            self.__hashtags__ = video_hashtags

        # extract profile name
        try:
            self.__profile_name__ = self.__info_json__['entry_data']['PostPage'][0]['graphql']['shortcode_media']['owner']['username']
        except (IndexError, KeyError):
            self.__profile_name__ = profile
        # canonical_href = soup.find('link', rel='canonical')['href']
        # canonical_href = canonical_href.replace(__INSTAGRAM_URL__, '')
        # self.__profile_name__ = canonical_href.split('/')[0]
        return

    def get_caption(self):
        if self.__info_json__ is None:
            return None
        try:
            caption = self.__info_json__['entry_data']['PostPage'][0]['graphql']['shortcode_media']['edge_media_to_caption']['edges'][0]['node']['text']
        except (IndexError, KeyError):
            return None
        return caption

    def save_caption(self):
        pass

    def get_photo(self, output_path, output_prefix='', with_feedback=True):
        if with_feedback:
            print('>>', self.__class__.__name__, 'get_photo')

        if self.__info_json__ is None:
            return

        output_prefix = output_prefix.strip()
        if len(output_prefix) > 0:
            output_prefix = output_prefix + '-'

        short_code_media = self.__info_json__['entry_data']['PostPage'][0]['graphql']['shortcode_media']

        # if multi photos are in a post, all photos are loaded and saved.
        # each photo gets an index.
        # file name format: [output_prefix][profile name]-[shortcode]-[index].[extension]
        if 'edge_sidecar_to_children' in short_code_media.keys():
            idx = 1
            for edge in short_code_media['edge_sidecar_to_children']['edges']:
                if edge['node']['__typename'] == 'GraphImage':
                    file_name = '{}{}-{}-{}{}'.format(output_prefix, self.__profile_name__, self.__shortcode__, idx, __EXT_JPG__)
                    simple_request.get_image(edge['node']['display_url'], os.path.join(output_path, file_name))
                    idx = idx + 1
        # single photo is in a post.
        # file name format: [output_prefix][profile name]-[shortcode].[extension]
        elif short_code_media['__typename'] == 'GraphImage':
            file_name = '{}{}-{}{}'.format(output_prefix, self.__profile_name__, self.__shortcode__, __EXT_JPG__)
            simple_request.get_image(short_code_media['display_url'], os.path.join(output_path, file_name))
        return

    def get_like_counts(self):
        if self.__info_json__ is None:
            return None
        try:
            # if post is video its views count is considered as likes
            if self.__info_json__['entry_data']['PostPage'][0]['graphql']['shortcode_media']['is_video']:
                count = self.__info_json__['entry_data']['PostPage'][0]['graphql']['shortcode_media']['video_view_count']
            else:
                count = self.__info_json__['entry_data']['PostPage'][0]['graphql']['shortcode_media']['edge_media_preview_like']['count']
        except (IndexError, KeyError):
            return None
        return count

    def get_comment_counts(self):
        if self.__info_json__ is None:
            return None
        try:
            count1 = self.__info_json__['entry_data']['PostPage'][0]['graphql']['shortcode_media']['edge_media_to_comment']['count']
        except (IndexError, KeyError):
            count1 = 0
        try:
            count2 = self.__info_json__['entry_data']['PostPage'][0]['graphql']['shortcode_media']['edge_media_preview_comment']['count']
        except (IndexError, KeyError):
            count2 = 0
        return count1 + count2

    def get_timestamp(self):
        if self.__info_json__ is None:
            return None
        try:
            ts = self.__info_json__['entry_data']['PostPage'][0]['graphql']['shortcode_media']['taken_at_timestamp']
        except (IndexError, KeyError):
            return None
        return ts

    # def get...(self, item):
    #     pass

# ##################################################################################

class InstaTasks:
    def get_hashtag_shorcodes(self, hashtag, scroll_limit=None, with_feedback=True):
        if with_feedback:
            print('>>', self.__class__.__name__, 'get_hashtag_shortcodes')

        # 1 scroll_limit = 12 posts
        # scroll_limit = None: all posts

        # I used Firefox; you can use whichever browser you like.
        browser = webdriver.Firefox(firefox_binary = '/opt/firefox-dev/firefox')

        extension_path = '/home/rasoul/.mozilla/firefox/m03saqxc.default/extensions/@hoxx-vpn.xpi'  # Must be the full path to an XPI file!
        browser.install_addon(extension_path, temporary=True)
        input('***** Setup proxy if needed and then press ENTER ...')

        # Tell Selenium to get the URL you're interested in.
        profile_url = os.path.join(__INSTAGRAM_TAGS_URL__, hashtag)
        browser.get(profile_url)

        # Selenium script to scroll to the bottom, wait 5 seconds for the next batch of data to load, then continue scrolling.
        # It will continue to do this until the page stops loading new data.
        len_of_page = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match = False
        limit = 0
        shortcodes = []
        while not match:
            last_count = len_of_page
            time.sleep(10)
            len_of_page = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            span = soup.find('span', id='react-root')
            if span:
                links = span.find_all('a', href=re.compile('/p/'))
                if links:
                    shortcodes = shortcodes + [l['href'] for l in links]
            if last_count == len_of_page:
                match = True

            # scroll_limit is used to prevent scrolling to the end of page.
            # if it is None, it means scroll to the end of page.
            limit = limit + 1
            if scroll_limit is not None:
                if limit >= scroll_limit:
                    break

        # removes duplicate shortcodes while maitains original order
        shortcodes = list(OrderedDict.fromkeys(shortcodes))
        shortcodes = [shortcode.replace('/p/', '').replace('/', '') for shortcode in shortcodes]
        return shortcodes

    def get_profiles_by_hashtag(self, hashtag, output_file, from_temp=False, scroll_limit=None, min_posts=0, min_followers=0, with_feedback=True):
        """
        fetches profiles based on a hashtag with min_posts and min_followers and
        generates a csv with profile_name, posts, followers and following columns.
        csv is saved in output_file.
        shortcodes reads from temp file if from_temp is true.
        temp file name is as "[output_file].tmp"
        """

        if with_feedback:
            print('>>', self.__class__.__name__, 'get_profiles_by_hashtag')
            print('\nFetching profiles with hashtag', hashtag)
            print('* Fetching shortcodes ...')

        if from_temp:
            # temp filename is as output_file + '.tmp'
            with open(output_file+__EXT_TEMP__) as f:
                codes = f.read()
                shortcodes = codes.split(' ')
        else:
            shortcodes = self.get_hashtag_shorcodes(hashtag, scroll_limit=scroll_limit)
            if not shortcodes:
                return
            # fetched shortcodes written in a file with name "[output_file].tmp"
            with open(output_file+__EXT_TEMP__, 'w') as f:
                f.write(' '.join(shortcodes))

        if with_feedback:
            print('* Fetching profiles for {} shorcodes ...'.format(len(shortcodes)))
        counter = 0
        profiles = {}
        for code in shortcodes:
            counter = counter + 1
            profile_name = InstaPost(None, code).__profile_name__
            if with_feedback:
                print('**', counter, code, profile_name)
            time.sleep(randint(1, 3))
            if profile_name in profiles:
                continue
            insta_profile = InstaProfile(profile_name)
            insta_profile.get_base_info()
            followers, following = insta_profile.get_followers_following()
            posts = insta_profile.get_posts_count()
            if posts >= min_posts and followers >= min_followers:
                profiles[profile_name] = [str(posts), str(followers), str(following)]
            # time.sleep(randint(2, 4))

        if with_feedback:
            print('* Writing results ...')
        with open(output_file, 'w') as f:
            f.write('profile, posts, followers, following\n')
            for profile_name in profiles:
                line = '{},{}\n'.format(profile_name, ','.join(profiles[profile_name]))
                f.write(line)
        return

# ##################################################################################

def get_profile_shortcodes():
    """
    Note: this script should be run on client. each run gets just ONE profile shortcodes.
    1. gets an unstarred profile name from profiles.txt
    2. connects to the profile
    3. retrieves all shorcodes and saves them in a file. file name is '[profile name].shortcode'
    4. puts star at the beginning of profile name and updates profiles.txt
    """
    # gets an unstarred profile name from profiles.txt
    try:
        with open(os.path.join(__BASE_PATH__, __CONTENT_PATH__, __PROFILES_FILE__), 'r') as f:
            profile_str = f.read()
        if not profile_str:
            return
        profile_names = profile_str.split('\n')
        current_profile = None
        for pn in profile_names:
            if pn[0] != '*':
                current_profile = pn
                break
        if current_profile is None:
            return
    except IOError as e:
        print(e)
        return

    # connects to profile
    # retrieves all shortcodes and saves them in file
    try:
        profile = InstaProfile(current_profile)
        profile.get_base_info()
        profile.get_posts_shorcodes(scroll_limit=50)
        profile.save_posts_shortcodes()
    except IOError as e:
        print(e)
        return
    
    # puts star at the beginning and current date at the end of profile name and updates profiles.txt
    try:
        profile_names.remove(current_profile)
        profile_names.append('*{}-{}'.format(current_profile, str(datetime.now())[:10]))
        profile_str = '\n'.join(profile_names)
        with open(os.path.join(__BASE_PATH__, __CONTENT_PATH__, __PROFILES_FILE__), 'w') as f:
            f.write(profile_str)
    except IOError as e:
        print(e)
    return

def get_profile_info():
    """
    Note: this script should be run on a server as a cron job. so each run gets just ONE profile info.
    1. gets an unstarred profile name from profiles.txt
    2. reads profile_name __shortcodes__ from file
    3. retrieves all captions and hashtags of each shortcode and saves them in files
    4. puts star at the beginning of profile name and updates profiles.txt
    """
    # gets an unstarred profile name from profiles.txt
    try:
        with open(os.path.join(__BASE_PATH__, __CONTENT_PATH__, __PROFILES_FILE__), 'r') as f:
            profile_str = f.read()
        if not profile_str:
            return
        profile_names = profile_str.split('\n')
        current_profile = None
        for pn in profile_names:
            if pn[0] != '*':
                current_profile = pn
                break
        if current_profile is None:
            return
    except IOError as e:
        print(e)
        return

    # reads profile_name __shortcodes__ from file
    # retrieves all captions and hashtags of each shortcode and saves them in files
    try:
        profile = InstaProfile(current_profile)
        profile.get_base_info()
        profile.read_posts_shortcodes()
        profile.save_posts_info()
    except IOError as e:
        print(e)
        return
    
    # puts star at the beginning of profile name and updates profiles.txt
    try:
        profile_names.remove(current_profile)
        profile_names.append('*'+current_profile)
        profile_str = '\n'.join(profile_names)
        with open(os.path.join(__BASE_PATH__, __CONTENT_PATH__, __PROFILES_FILE__), 'w') as f:
            f.write(profile_str)
    except IOError as e:
        print(e)
    return

if __name__ == "__main__":
    pass

    # call get_profile_shortcodes() to retrieve first unstarred profile from profiles.txt
    # get_profile_shortcodes()
    # exit(0)

    ### must be called on server get_profile_info()
    # get_profile_info()

    ### generates word cloud for a profile based on captions
    # ip = InstaProfile('shaghayeghfarahani')
    # ip.generate_caption_wordcloud(font_path=__FONT_ZIBA__,
    #                               mask=WCGenerator.circle_mask(800),
    #                             #   mask=WCGenerator.image_mask(os.path.join(__BASE_PATH__, __IMAGE_PATH__, 'bijan_banafshehkhah-Bm9NkEcFBsF.jpg')),
    #                               background_color='white', repeat=False, scale=2,
    #                               colormap=matplotlib.cm.get_cmap('Dark2'),
    #                               contour_width=0, contour_color='black',
    #                               color_func=None)
    # exit(0)

    ### generates word cloud for a profile based on hashtags
    # ip = InstaProfile('shaghayeghfarahani')
    # ip.generate_hashtag_wordcloud(font_path=__FONT_ZIBA__,
    #                               mask=WCGenerator.circle_mask(800),
    #                               background_color='black', repeat=True, scale=2,
    #                               colormap=matplotlib.cm.get_cmap('Set2'),
    #                               contour_width=0, contour_color='black', color_func=None)
    # exit(0)

    ### retrieves photo of a post shortcode and generates its snowy photo.
    profile = ''
    # shortcode = 'BfoYLoWnz8V'
    # InstaPost(profile, shortcode).get_photo(os.path.join(__BASE_PATH__, __IMAGE_PATH__))
    shortcodes = [
        'B4zVqPtBzaE',
    ]
    for sh in shortcodes:
        InstaPost(profile, sh).get_photo(os.path.join(__BASE_PATH__, __IMAGE_PATH__, 'origin'), output_prefix='mix07')
    exit(0)

    file_name = '{}-{}'.format(profile, shortcode)
    # file_name = 'landscape-2'
    file_name_index = 1
    sharpness_percent = 30
    resize_percent = 50

    input_image = './images/{}.jpg'.format(file_name)
    output_image = './outputs/{}-{}.png'
    
    snowy_img = SnowyImage(origin_file=input_image)
    snowy_img.pattern(pattern_type='x', pattern_size=6, background_color='white', from_origin=True). \
        sharpness(sharpness_percent).save(output_image.format(file_name, file_name_index), resize_percent=resize_percent)
    snowy_img.pattern(pattern_type='o', pattern_size=5, background_color='white', from_origin=True, random_pixles_percent=20). \
        sharpness(sharpness_percent).save(output_image.format(file_name, file_name_index+1), resize_percent=resize_percent)

    min_text, max_text = 'هانیه‌توسلی', 'هانیه'
    # min_text, max_text = 'لیلااوتادی', 'لیلا'
    # min_text, max_text = 'مهراوه‌شریفی‌نیا', 'مهراوه'
    min_font = ImageFont.truetype('pixelboy-BJadidBold.ttf', size=10)
    max_font = ImageFont.truetype('pixelboy-BJadidBold.ttf', size=420)
    min_text, max_text = PersianText.reshape(min_text), PersianText.reshape(max_text)
    # min_text, max_text = 'NAZANIN♥BAYATI♥', 'NAZANIN'
    # min_font = ImageFont.truetype('impact.ttf', size=7)
    # max_font = ImageFont.truetype('impact.ttf', size=260)

    # snowy_img.solid_text_mask(min_text, min_font, from_origin=True, background_color='white', alpha=255)
    snowy_img.pattern(background_color='white', pattern_size=7, from_origin=True)
    # snowy_img.pattern(pattern_type='o', pattern_size=4, background_color='white', from_origin=True, random_pixles_percent=15)
    max_img = SnowyImage(input_image).text_mask(max_text, max_font, from_origin=True, alpha=90)
    snowy_img.set_over(max_img)
    snowy_img.sharpness(sharpness_percent).save(output_image.format(file_name, file_name_index+2), resize_percent=resize_percent)

    transparent_font = ImageFont.truetype('impact.ttf', size=370)
    transparent_img = SnowyImage(input_image).solid_text_mask(max_text, transparent_font, from_origin=True, alpha=150)
    SnowyImage(input_image).set_over(transparent_img).sharpness(sharpness_percent). \
        save(output_image.format(file_name, file_name_index+3), resize_percent=resize_percent)

    SnowyImage(input_image).solid_text_mask(min_text, min_font, from_origin=True, background_color='white'). \
        sharpness(sharpness_percent).save(output_image.format(file_name, file_name_index+4), resize_percent=resize_percent)

    SnowyImage(input_image). \
        gamma_brighten(from_origin=True, repeat=2). \
        remove_noise(from_origin=False, repeat=3). \
        sharpen(from_origin=False, repeat=9). \
        save(output_image.format(file_name, file_name_index+5), resize_percent=resize_percent)
    SnowyImage(output_image.format(file_name, file_name_index+5)). \
        sharpen(from_origin=True, repeat=2).save(output_image.format(file_name, file_name_index+6))

    temp_file = './outputs/~~~temp.png'
    SnowyImage(input_image). \
        gamma_brighten(from_origin=True, repeat=1). \
        remove_noise(from_origin=False, repeat=1).save(temp_file)
    cartoonizer.cartoonize(temp_file, output_image.format(file_name, file_name_index+7), contour_thikness=0)
    SnowyImage(output_image.format(file_name, file_name_index+7)). \
        save(output_image.format(file_name, file_name_index+7), resize_percent=resize_percent)

    # # #profile = InstaProfile('honarmandan._irani')
    # # #profile.generate_snowy_photo('BuhNIYmHj7O', photo_enhance_factor=2, photo_exists=True)

    ###################################################################################################
    ###################################################################################################

    # ip.get_posts_shorcodes(scroll_limit=None)
    # ip.save_posts_shortcodes()
    # ip.save_posts_info(append=True)
    # ip.read_posts_shortcodes()
    # print(ip.get_all_hashtags())
    # print(ip.get_persian_hashtags())
    # print(ip.__shortcodes__)
    
    # post = InstaPost('amir_mahdi_jule', 'BtdFi2BFjIW')
    # post = InstaPost('haniehtavassoli', 'BlmilErHY53')
    # post = InstaPost('haniehtavassoli', 'BkOBXy3Hs9Z')
    # post = InstaPost('anahitahemmati', '1kFo-RJYDb')
    # post = InstaPost('nazy_kh', 'Btnbcr3nt25')
    # post = InstaPost('_sahardolatshahi', 'BqdaEfpleaw')
    # print(post.get_caption())
    # post.get_photo(os.path.join(__BASE_PATH__, __IMAGE_PATH__))

    # post = InstaPost('tagneshan.ir', 'BtnESztHQ6T')
    # post = InstaPost('mowjonline', 'Btn1ZUAn8_f')
    # print(post.__hashtags__)

