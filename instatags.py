from bs4 import BeautifulSoup
import json
from bidi.algorithm import get_display
from arabic_reshaper import ArabicReshaper
import re
import os
import time
from random import randint
import matplotlib
from PIL import ImageFont
import simple_request
from wordcloud_generator import WCGenerator
from persiantext import PersianText

###### class InstagramTags ######
class InstagramTags:
    def __init__(self, profile_url, post_limit=4, with_feedback=True):
        if with_feedback:
            print('>>', self.__class__.__name__, '__init__', profile_url)

        self.post_limit = post_limit
        self.posts_info = None
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
        profile_info = json.loads(info_script[0][json_start:json_end+1])
        self.posts_info = profile_info['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']
        time.sleep(randint(5, 10))
        return
        
    def get_post_hashtags(self, shortcode, with_feedback=True):
        if with_feedback:
            print('>>', self.__class__.__name__, 'get_post_hashtags', shortcode)
            
        url = 'https://www.instagram.com/p/' + shortcode
        html = simple_request.simple_get(url)
        time.sleep(randint(3, 6))
        if html is None:
            return None
        soup = BeautifulSoup(html, 'html.parser')
        hashtags = [meta['content'] for meta in soup.find_all('meta', property='instapp:hashtags')]
        video_hashtags = [meta['content'] for meta in soup.find_all('meta', property='video:tag')]
        if hashtags and video_hashtags:
            return hashtags + video_hashtags
        elif hashtags:
            return hashtags
        elif video_hashtags:
            return video_hashtags
        return None
    
    def get_all_hashtags(self):
        if self.posts_info is None:
            return None
        selected_posts = self.posts_info if self.post_limit > len(self.posts_info) else self.posts_info[:self.post_limit]
        hashtags = []
        for post in selected_posts:
            ht = self.get_post_hashtags(post['node']['shortcode'])
            if ht is not None:
                hashtags = hashtags + ht
        if len(hashtags) == 0:
            return None
        return hashtags
    
    def get_persian_hashtags(self, replace_underline_with='-'):
        tags = self.get_all_hashtags()
        if tags is None:
            return None
        reshaper_config = {'language': 'Farsi', 'RIAL SIGN': True}
        reshaper = ArabicReshaper(reshaper_config)
        tags = [get_display(reshaper.reshape(t)) for t in tags]
        tags = [t.replace('_', replace_underline_with) for t in tags]
        tags = [t for t in tags if re.search('[a-zA-Z]', t) is None]   # removes tags with english letters
        if len(tags) == 0:
            return None
        return tags

    def get_shortcodes(self):
        if self.posts_info is None:
            return None
        selected_posts = self.posts_info if self.post_limit > len(self.posts_info) else self.posts_info[:self.post_limit]
        shortcodes = []
        for post in selected_posts:
            shortcodes.append(post['node']['shortcode'])
        return shortcodes
    

###### function generate profiles word cloud from profile urls in a text file ######
def generate_profiles_wordcloud(profiles_file, font_path=None, mask=None, background_color='black',
                                colormap=None, contour_width=0, contour_color='black', repeat=False, scale=2, color_func=None,
                                output_file=None, display_online=False, post_limit=4):
    with open(profiles_file) as pf_file:
        profiles = pf_file.readlines()
        
    all_tags = []
    if profiles:
        for p in profiles:
            pr = p.strip()
            if not pr:
                continue
                
            # '*' at the beginnig of a profile url means it does not need to scrape it
            if pr[0] == '*':
                continue
            ptags = InstagramTags(pr, post_limit=post_limit).get_persian_hashtags()
            if ptags is not None:
                all_tags = all_tags + ptags
        if len(all_tags) > 0:
            WCGenerator(all_tags).generate(display_online=display_online, font_path=font_path, colormap=colormap,
                                           output_file=output_file, mask=mask, repeat=repeat, scale=scale,
                                           background_color=background_color, contour_width=contour_width,
                                           contour_color=contour_color, color_func=color_func)
            # write all tags in a file with name same as png file with 'tags' extension.
            # it can be used to generate new word clouds without scraping again.
            with open(output_file+'.tags', 'w') as f:
                f.write(' '.join(all_tags))

def get_profiles_hashtags(profiles_file, output_file, post_limit=4):
    with open(profiles_file) as pf_file:
        profiles = pf_file.readlines()
        
    all_tags = []
    if profiles:
        for p in profiles:
            pr = p.strip()
            if not pr:
                continue
                
            # '*' at the beginnig of a profile url means it does not need to scrape it
            if pr[0] == '*':
                continue
            ptags = InstagramTags(pr, post_limit=post_limit).get_persian_hashtags()
            if ptags is not None:
                all_tags = all_tags + ptags

            with open(output_file, 'w') as f:
                f.write(' '.join(all_tags))
    return

###### MAIN SECTION ######
if __name__ == "__main__":
    pass

####################################################
    def is_part_of(item, item_list):
        for x in item_list:
            if x in item:
                return True
        return False
####################################################

    abs_path = '.'
    outputs_path = '{}/outputs/'.format(abs_path)
    mask_images_path = '{}/images/'.format(abs_path)
    # font_path = '{}/fonts/pixelboy-BZiba.ttf'.format(abs_path)
    # font_path = '{}/fonts/AdobeArabic-Bold.otf'.format(abs_path)
    # font_path = '{}/fonts/Arghavan.ttf'.format(abs_path)
    font_path = '{}/fonts/B Araz.ttf'.format(abs_path)
    profiles_file = '{}/profiles/cinema.txt'.format(abs_path)
    tags_file = outputs_path + '__cinema.tags'
    reshaped_tags_file = outputs_path + '__cinema-reshaped.tags'

    # comment below line to regenerate word cloud with new params from existing tags file.
    # get_profiles_hashtags(profiles_file, tags_file, post_limit=3)

    reshaper_config = {'language': 'Farsi', 'RIAL SIGN': True}
    reshaper = ArabicReshaper(reshaper_config)
    excludes = ['فجر', 'ایران', 'جشنواره', 'بازیگر', 'هنر', 'عکاس', 'پرتره',
                'فيلم', 'فیلم', 'دیالوگ-نیوز', 'عکس', 'اینستاگرام', 'مدل',
                'سينما', 'سینما', 'زن', 'سلبریتی', 'باز', 'آنلاین', 'نما', 'استایل',
                'سریال', 'سريال', 'عكس', 'عكاسي', 'متین', 'متين', 'سودای', 'سوداي',
                'مردانه', 'زنانه', 'لباس', 'اکران', 'اكران', 'مو', 'کارگردان', 'كارگردان',
                'سوپراستار', 'زیبا', 'زيبا', 'صداوسیما', 'تئاتر', 'سلبریتیها', 'آرایش', 'گریم',
                'گیس', 'خوشگل', 'زنان', 'مردان', 'تاتر', 'تبلیغ', 'تبلیغات', 'مدلینگ', 'کنسرت',
                'تلویزیون', 'دخترونه', 'تیپ', 'میکاپ', 'دابسمش', 'فوتبال', 'صحنه', 'فشن',
                'حاشیه', 'عصر', 'علیخانی', 'برنده', 'گلزار', 'مدیری', # 'عصر', 'مدیر', 'علیخانی', 'ژن', 'نازنین', 'الناز', 'خندوانه', 'افسانه', 'ستاره', 'خشایار',
                'خواننده', 'زمستان'
                ]
    reshaped_excludes = [get_display(reshaper.reshape(t)) for t in excludes]
    with open(tags_file, 'r') as f:
        tags_str = f.read()
    tags = tags_str.split(' ')
    tags = [t for t in tags if not is_part_of(t, reshaped_excludes)]
    with open(reshaped_tags_file, 'w') as f:
        f.write(' '.join(tags))

    result_file = WCGenerator.generate_output_filename(outputs_path)
    WCGenerator(from_file=reshaped_tags_file) \
                .generate(font_path=font_path,
                        #   mask=WCGenerator.image_mask(mask_images_path+'frame-8.png'),
                          mask=WCGenerator.circle_mask(800),
                          colormap=matplotlib.cm.get_cmap(name='Dark2'),
                          output_file=result_file,
                          display_online=True, contour_color='black', contour_width=0, scale=2,
                          background_color='white'
                        #   color_func=WCGenerator.single_color('black')
                        #   color_func=WCGenerator.single_color(rgb=(100, 100, 100))
                          )
    WCGenerator.draw_text_on_image(result_file, '@tagneshan.ir', font=ImageFont.truetype('arial.ttf', size=50), location='bottom left', color='red')
    WCGenerator.draw_text_on_image(result_file, PersianText.reshape('هشتگ‌های داغ سینمایی'), font=ImageFont.truetype(font_path, size=50), location='bottom right', color='red')
