import matplotlib.cm
import matplotlib.pyplot as plt
import os
import pandas as pd
import pystagram
from PIL import Image, ImageFont
from pystagram import InstaProfile
from persiantext import PersianText
from wordcloud_generator import WCGenerator

output_path = './outputs/'
font_path = './fonts/AdobeArabic-Bold.otf'

def merge_images(image_files, result_file, title=None, direction='vertical'):
    y = 0 if title is None else 70
    images = [Image.open(f) for f in image_files]
    if direction.lower() == 'vertical':
        new_width = max([img.width for img in images])
        new_height = sum([img.height for img in images]) + y
        new_image = Image.new('RGBA', (new_width, new_height), color='white')
        for img in images:
            new_image.paste(img, (0, y))
            y = y + img.height
    else:
        new_width = sum([img.width for img in images])
        new_height = max([img.height for img in images]) + y
        new_image = Image.new('RGBA', (new_width, new_height), color='white')
        x = 0
        for img in images:
            new_image.paste(img, (x, y))
            x = x + img.width
    new_image.save(result_file)
    if title is not None:
        title = PersianText.reshape(title)
        WCGenerator.draw_text_on_image(result_file, title, font=ImageFont.truetype(font_path, size=50), location='top center', color='red')
    return

def analyze_profile(profile_name, new_scrape=False, scroll_limit=1, chart_base_size_inch=5):
    """
    each scroll_limit is 12 posts and None means all posts of profile.
    """
    font_size = 4 * chart_base_size_inch
    max_tokens = 50
    is_demo = False
    if scroll_limit is None:
        file_path = output_path + profile_name + '.all-'
    else:
        file_path = output_path + profile_name + '.' + str(scroll_limit) + '-'
        # scroll_limit <= 2 assumes as demo version of analysis
        if scroll_limit <= 2:
            max_tokens = 15
            is_demo = True

    caption_wcloud_file = file_path + '01.caption-cloud.png'
    caption_chart_file = file_path + '04.caption-chart.png'
    caption_treemap_file = file_path + '03.caption-treemap.png'
    hashtag_wcloud_file = file_path + '02.hashtag-cloud.png'
    hashtag_chart_file = file_path + '06.hashtag-chart.png'
    hashtag_treemap_file = file_path + '05.hashtag-treemap.png'
    day_aggregate_file = file_path + '10.aggregate-day.png'
    hour_aggregate_file = file_path + '09.aggregate-hour.png'
    like_hashtag_file = file_path + '08.hashtag-like.png'
    comment_hashtag_file = file_path + '07.hashtag-comment.png'
    day_hour_like_heatmap_file = file_path + '11.heatmap-like.png'
    day_hour_comment_heatmap_file = file_path + '12.heatmap-comment.png'
    report_file = file_path + '13.report.png'
    all_in_one_file = file_path + '00.allinone.png'

    profile = InstaProfile(profile_name)
    if new_scrape:
        try:
            profile.get_base_info()
            print('Fetching shortcodes ...')
            profile.get_posts_shorcodes(scroll_limit=scroll_limit)
            profile.save_posts_shortcodes()
            profile.read_posts_shortcodes(append=False)
            print('Fetching posts captions ...')
            profile.save_posts_info(append=False)
        except IOError as e:
            print(e)
    else:
        profile.read_base_info()

    print('Generating charts ...')

    width = 1.5 * chart_base_size_inch
    height = chart_base_size_inch

    profile.generate_day_hour_heatmaps(width_inch=1.5*width, height_inch=height, likes_save_to=day_hour_like_heatmap_file, comments_save_to=day_hour_comment_heatmap_file)
    WCGenerator.draw_text_on_image(day_hour_like_heatmap_file, '@tagneshan.ir', font=ImageFont.truetype('arial.ttf', size=font_size), location='top right', color='red')
    WCGenerator.draw_text_on_image(day_hour_comment_heatmap_file, '@tagneshan.ir', font=ImageFont.truetype('arial.ttf', size=font_size), location='top right', color='red')
    profile.generate_day_aggregate_charts(width_inch=1.5*width, height_inch=height, save_to=day_aggregate_file, \
        font_name=font_path, color=['darkorange', 'maroon'])
    WCGenerator.draw_text_on_image(day_aggregate_file, '@tagneshan.ir', font=ImageFont.truetype('arial.ttf', size=font_size), location='bottom left', color='red')
    profile.generate_hour_aggregate_charts(width_inch=1.5*width, height_inch=height, save_to=hour_aggregate_file, \
        font_name=font_path, color=['peru', 'navy'])
    WCGenerator.draw_text_on_image(hour_aggregate_file, '@tagneshan.ir', font=ImageFont.truetype('arial.ttf', size=font_size), location='bottom left', color='red')
    profile.generate_hashtags_charts(sum_col='likes', max_hashtags=max_tokens, \
        title='متوسط تعداد لایک‌ها به ازای هشتگ‌ها', xlabel='هشتگ‌ها', ylabel='تعداد لایک', width_inch=1.5*width, height_inch=height, \
        font_name=font_path, legend_labels=['لایک'], save_to=like_hashtag_file, color='seagreen')
    WCGenerator.draw_text_on_image(like_hashtag_file, '@tagneshan.ir', font=ImageFont.truetype('arial.ttf', size=font_size), location='bottom left', color='red')
    profile.generate_hashtags_charts(sum_col='comments', max_hashtags=max_tokens, \
        title='متوسط تعداد کامنت‌ها به ازای هشتگ‌ها', xlabel='هشتگ‌ها', ylabel='تعداد کامنت', width_inch=1.5*width, height_inch=height, \
        font_name=font_path, legend_labels=['کامنت'], save_to=comment_hashtag_file, color='steelblue')
    WCGenerator.draw_text_on_image(comment_hashtag_file, '@tagneshan.ir', font=ImageFont.truetype('arial.ttf', size=font_size), location='bottom left', color='red')
    profile.generate_summary_report(is_demo=is_demo, save_to=report_file)

    captions_file = profile.captions_filename()
    if not os.path.exists(captions_file):
        print('{} not found!'.format(captions_file))
    else:
        text = ''
        with open(captions_file, 'r') as f:
            text = f.read()
        # stop_words = [['نمی', 'هایی', 'های', 'اند', 'کردن', 'ترین', 'مان', 'هایش']]
        pt = PersianText(text) \
            .replace([('\n', ' '), (pystagram.__SEPARATOR__, ' '), ('_', '-'), ('ك', 'ک'), ('ي', 'ی')]) \
            .tokenize() \
            .filter_tokens(pos_tags=['N'], language=None, min_len=3, reshape=True, stop_words=[['های']])
        pt.generate_wordcloud(
            font_path=font_path, mask=WCGenerator.circle_mask(100*width),
            background_color='white', scale=1, colormap=matplotlib.cm.get_cmap('tab10'),
            display_online=False, output_file=caption_wcloud_file,
            output_file_sign={'text': '@tagneshan.ir', 'location': 'bottom left', 'color': 'red', 'font': ImageFont.truetype('arial.ttf', size=font_size)},
            output_file_text={'text': 'ابرواژگان واژه‌ها', 'location': 'top center', 'color': 'red', 'font': ImageFont.truetype('AdobeArabic-Bold.otf', size=font_size)})
        pt.barchart(max_tokens, width_inch=width, height_inch=width, title='فراوانی واژه‌ها', save_to=caption_chart_file, font_name=font_path, color='brown')
        WCGenerator.draw_text_on_image(caption_chart_file, '@tagneshan.ir', font=ImageFont.truetype('arial.ttf', size=font_size), location='top right', color='red')
        pt.treemap(max_tokens, width_inch=width, height_inch=width, title='فراوانی واژه‌ها', save_to=caption_treemap_file, font_name=font_path)
        WCGenerator.draw_text_on_image(caption_treemap_file, '@tagneshan.ir', font=ImageFont.truetype('arial.ttf', size=font_size), location='bottom left', color='red')

    hashtags_file = profile.hashtags_filename()
    if not os.path.exists(hashtags_file):
        print('{} not found!'.format(hashtags_file))
    else:
        text = ''
        with open(hashtags_file, 'r') as f:
            text = f.read()
        pt = PersianText(text) \
            .replace([('_', '-'), ('ك', 'ک'), ('ي', 'ی')]) \
            .tokenize() \
            .filter_tokens(language=None, min_len=3, reshape=True)
        pt.generate_wordcloud(
            font_path=font_path, mask=WCGenerator.circle_mask(100*width),
            background_color='white', scale=1, colormap=matplotlib.cm.get_cmap('Dark2'),
            display_online=False, output_file=hashtag_wcloud_file,
            output_file_sign={'text': '@tagneshan.ir', 'location': 'bottom left', 'color': 'red', 'font': ImageFont.truetype('arial.ttf', size=font_size)},
            output_file_text={'text': 'ابرواژگان هشتگ‌ها', 'location': 'top center', 'color': 'red', 'font': ImageFont.truetype('AdobeArabic-Bold.otf', size=font_size)})
        pt.barchart(max_tokens, width_inch=width, height_inch=width, title='فراوانی هشتگ‌ها', save_to=hashtag_chart_file, font_name=font_path, color='orange')
        WCGenerator.draw_text_on_image(hashtag_chart_file, '@tagneshan.ir', font=ImageFont.truetype('arial.ttf', size=font_size), location='top right', color='red')
        pt.treemap(max_tokens, width_inch=width, height_inch=width, title='فراوانی هشتگ‌ها', save_to=hashtag_treemap_file, font_name=font_path)
        WCGenerator.draw_text_on_image(hashtag_treemap_file, '@tagneshan.ir', font=ImageFont.truetype('arial.ttf', size=font_size), location='bottom left', color='red')

        # generating all in one charts
        tmp1 = output_path + '~~~tmp1.png'
        tmp2 = output_path + '~~~tmp2.png'
        tmp3 = output_path + '~~~tmp3.png'
        tmp4 = output_path + '~~~tmp4.png'
        tmp5 = output_path + '~~~tmp5.png'

        merge_images([caption_chart_file, caption_treemap_file, caption_wcloud_file], tmp1, title='فراوانی واژه‌ها', direction='horizontal')
        merge_images([hashtag_chart_file, hashtag_treemap_file, hashtag_wcloud_file], tmp2, title='فراوانی هشتگ‌ها', direction='horizontal')

        merge_images([like_hashtag_file, comment_hashtag_file], tmp3, title='', direction='horizontal')
        merge_images([day_aggregate_file, hour_aggregate_file], tmp4, title='', direction='horizontal')
        merge_images([day_hour_comment_heatmap_file, day_hour_like_heatmap_file], tmp5, title='', direction='horizontal')

        merge_images([tmp1, tmp2, tmp3, tmp4, tmp5], all_in_one_file, title=profile_name, direction='vertical')
        return

def generate_charts(profile_name, new_scrape=False, demo=True, chart_base_size_inch=5):
    """
    it is DEPRECATED.
    analyze_profile is updated version.
    """
    font_size = 4 * chart_base_size_inch
    if demo:
        scroll_limit = 1
        max_tokens = 10
        caption_wcloud_file = output_path + profile_name + '.demo-01.caption-cloud.png'
        caption_chart_file = output_path + profile_name + '.demo-04.caption-chart.png'
        caption_treemap_file = output_path + profile_name + '.demo-03.caption-treemap.png'
        hashtag_wcloud_file = output_path + profile_name + '.demo-02.hashtag-cloud.png'
        hashtag_chart_file = output_path + profile_name + '.demo-06.hashtag-chart.png'
        hashtag_treemap_file = output_path + profile_name + '.demo-05.hashtag-treemap.png'
        day_aggregate_file = output_path + profile_name + '.demo-10.aggregate-day.png'
        hour_aggregate_file = output_path + profile_name + '.demo-09.aggregate-hour.png'
        like_hashtag_file = output_path + profile_name + '.demo-08.hashtag-like.png'
        comment_hashtag_file = output_path + profile_name + '.demo-07.hashtag-comment.png'
        report_file = output_path + profile_name + '.demo-11.report.png'
    else:
        scroll_limit = None
        max_tokens = 50
        caption_wcloud_file = output_path + profile_name + '.main-01.caption-cloud.png'
        caption_chart_file = output_path + profile_name + '.main-04.caption-chart.png'
        caption_treemap_file = output_path + profile_name + '.main-03.caption-treemap.png'
        hashtag_wcloud_file = output_path + profile_name + '.main-02.hashtag-cloud.png'
        hashtag_chart_file = output_path + profile_name + '.main-06.hashtag-chart.png'
        hashtag_treemap_file = output_path + profile_name + '.main-05.hashtag-treemap.png'
        day_aggregate_file = output_path + profile_name + '.main-10.aggregate-day.png'
        hour_aggregate_file = output_path + profile_name + '.main-09.aggregate-hour.png'
        like_hashtag_file = output_path + profile_name + '.main-08.hashtag-like.png'
        comment_hashtag_file = output_path + profile_name + '.main-07.hashtag-comment.png'
        report_file = output_path + profile_name + '.main-11.report.png'

    profile = InstaProfile(profile_name)
    if new_scrape:
        try:
            profile.get_base_info()
            print('Fetching shortcodes ...')
            profile.get_posts_shorcodes(scroll_limit=scroll_limit)
            profile.save_posts_shortcodes()
            profile.read_posts_shortcodes(append=False)
            print('Fetching posts captions ...')
            profile.save_posts_info(append=False)
        except IOError as e:
            print(e)

    print('Generating charts ...')

    width = 1.5 * chart_base_size_inch
    height = chart_base_size_inch

    profile.generate_day_aggregate_charts(width_inch=1.5*width, height_inch=height, save_to=day_aggregate_file, \
        font_name=font_path, color=['darkorange', 'maroon'])
    WCGenerator.draw_text_on_image(day_aggregate_file, '@tagneshan.ir', font=ImageFont.truetype('arial.ttf', size=font_size), location='bottom left', color='red')
    profile.generate_hour_aggregate_charts(width_inch=1.5*width, height_inch=height, save_to=hour_aggregate_file, \
        font_name=font_path, color=['peru', 'navy'])
    WCGenerator.draw_text_on_image(hour_aggregate_file, '@tagneshan.ir', font=ImageFont.truetype('arial.ttf', size=font_size), location='bottom left', color='red')
    profile.generate_hashtags_charts(sum_col='likes', max_hashtags=max_tokens, \
        title='تعداد لایک‌ها به ازای هشتگ‌ها', xlabel='هشتگ‌ها', ylabel='تعداد لایک', width_inch=1.5*width, height_inch=height, \
        font_name=font_path, legend_labels=['لایک'], save_to=like_hashtag_file, color='seagreen')
    WCGenerator.draw_text_on_image(like_hashtag_file, '@tagneshan.ir', font=ImageFont.truetype('arial.ttf', size=font_size), location='bottom left', color='red')
    profile.generate_hashtags_charts(sum_col='comments', max_hashtags=max_tokens, \
        title='تعداد کامنت‌ها به ازای هشتگ‌ها', xlabel='هشتگ‌ها', ylabel='تعداد کامنت', width_inch=1.5*width, height_inch=height, \
        font_name=font_path, legend_labels=['کامنت'], save_to=comment_hashtag_file, color='steelblue')
    WCGenerator.draw_text_on_image(comment_hashtag_file, '@tagneshan.ir', font=ImageFont.truetype('arial.ttf', size=font_size), location='bottom left', color='red')
    profile.generate_summary_report(is_demo=demo, save_to=report_file)

    captions_file = profile.captions_filename()
    if not os.path.exists(captions_file):
        print('{} not found!'.format(captions_file))
    else:
        text = ''
        with open(captions_file, 'r') as f:
            text = f.read()
        # stop_words = [['نمی', 'هایی', 'های', 'اند', 'کردن', 'ترین', 'مان', 'هایش']]
        pt = PersianText(text) \
            .replace([('\n', ' '), (pystagram.__SEPARATOR__, ' '), ('_', '-'), ('ك', 'ک'), ('ي', 'ی')]) \
            .tokenize() \
            .filter_tokens(pos_tags=['N'], language=None, min_len=3, reshape=True, stop_words=[['های']])
        pt.generate_wordcloud(
            font_path=font_path, mask=WCGenerator.circle_mask(100*width),
            background_color='white', scale=1, colormap=matplotlib.cm.get_cmap('tab10'),
            display_online=False, output_file=caption_wcloud_file,
            output_file_sign={'text': '@tagneshan.ir', 'location': 'bottom left', 'color': 'red', 'font': ImageFont.truetype('arial.ttf', size=font_size)},
            output_file_text={'text': 'ابرواژگان واژه‌ها', 'location': 'top center', 'color': 'red', 'font': ImageFont.truetype('AdobeArabic-Bold.otf', size=font_size)})
        pt.barchart(max_tokens, width_inch=width, height_inch=width, title='فراوانی واژه‌ها', save_to=caption_chart_file, font_name=font_path, color='brown')
        WCGenerator.draw_text_on_image(caption_chart_file, '@tagneshan.ir', font=ImageFont.truetype('arial.ttf', size=font_size), location='top right', color='red')
        pt.treemap(max_tokens, width_inch=width, height_inch=width, title='فراوانی واژه‌ها', save_to=caption_treemap_file, font_name=font_path)
        WCGenerator.draw_text_on_image(caption_treemap_file, '@tagneshan.ir', font=ImageFont.truetype('arial.ttf', size=font_size), location='bottom left', color='red')

    hashtags_file = profile.hashtags_filename()
    if not os.path.exists(hashtags_file):
        print('{} not found!'.format(hashtags_file))
    else:
        text = ''
        with open(hashtags_file, 'r') as f:
            text = f.read()
        pt = PersianText(text) \
            .replace([('_', '-'), ('ك', 'ک'), ('ي', 'ی')]) \
            .tokenize() \
            .filter_tokens(language=None, min_len=3, reshape=True)
        pt.generate_wordcloud(
            font_path=font_path, mask=WCGenerator.circle_mask(100*width),
            background_color='white', scale=1, colormap=matplotlib.cm.get_cmap('Dark2'),
            display_online=False, output_file=hashtag_wcloud_file,
            output_file_sign={'text': '@tagneshan.ir', 'location': 'bottom left', 'color': 'red', 'font': ImageFont.truetype('arial.ttf', size=font_size)},
            output_file_text={'text': 'ابرواژگان هشتگ‌ها', 'location': 'top center', 'color': 'red', 'font': ImageFont.truetype('AdobeArabic-Bold.otf', size=font_size)})
        pt.barchart(max_tokens, width_inch=width, height_inch=width, title='فراوانی هشتگ‌ها', save_to=hashtag_chart_file, font_name=font_path, color='orange')
        WCGenerator.draw_text_on_image(hashtag_chart_file, '@tagneshan.ir', font=ImageFont.truetype('arial.ttf', size=font_size), location='top right', color='red')
        pt.treemap(max_tokens, width_inch=width, height_inch=width, title='فراوانی هشتگ‌ها', save_to=hashtag_treemap_file, font_name=font_path)
        WCGenerator.draw_text_on_image(hashtag_treemap_file, '@tagneshan.ir', font=ImageFont.truetype('arial.ttf', size=font_size), location='bottom left', color='red')

        if demo:
            tmp1 = output_path + '~~~tmp1.png'
            tmp2 = output_path + '~~~tmp2.png'
            tmp3 = output_path + '~~~tmp3.png'
            tmp4 = output_path + '~~~tmp4.png'

            merge_images([caption_chart_file, caption_treemap_file, caption_wcloud_file], tmp1, title='فراوانی واژه‌ها', direction='horizontal')
            merge_images([hashtag_chart_file, hashtag_treemap_file, hashtag_wcloud_file], tmp2, title='فراوانی هشتگ‌ها', direction='horizontal')

            merge_images([like_hashtag_file, comment_hashtag_file], tmp3, title='', direction='horizontal')
            merge_images([day_aggregate_file, hour_aggregate_file], tmp4, title='', direction='horizontal')

            merge_images([tmp1, tmp2, tmp3, tmp4], output_path+profile_name+'.demo.png', title=profile_name, direction='vertical')
        return

if __name__ == "__main__":
    pass

    # generate_charts('tag.nama', new_scrape=False, demo=False, chart_base_size_inch=5)
    profiles = [ \
        # 'antiqehome'
        # 'aradmachinery'
        # 'aradtravel'
        # 'arameshe_tabiat'
        # 'arameshsafar'
        # 'arashkalantari.ak'
        # 'arayeh_jwelery'
        # 'arayeshi_behdashti_darkhah'
        # 'archiwood_ind'
        # 'aria_technicaloffice'
        # 'armen.foods'
        # ---------------------------
        # 'art.baran.niakan'
        # 'arttex_ir'
        # 'arvin_clinic'
        # 'aryan.aghili'
        # 'arzjadid'
        # 'arzmodern'
        # 'asare.mosbat'
        # 'asatideonline'
        # 'ashkan.mlp'
        # 'ashraafcarpet'
        # 'auto_tabrizi'
        # 'ava_office_ahvaz'
        # 'azinedoor'
        # 'azingasht'
        # 'azar__kiani'
        # 'ashkanian_3'
        ]
    # for p in profiles:
    #     print('*****', p)
    #     analyze_profile(p, new_scrape=True, scroll_limit=1, chart_base_size_inch=3)
        # generate_charts(p, new_scrape=True, demo=True, chart_base_size_inch=4)

    analyze_profile('axneshan', new_scrape=False, scroll_limit=5, chart_base_size_inch=5)
    # analyze_profile('madjidnasiri', new_scrape=True, scroll_limit=5, chart_base_size_inch=5)
    # analyze_profile('iaukhshb', new_scrape=False, scroll_limit=None, chart_base_size_inch=5)

    # ----------------------------------------------------------------------------

    # ip = InstaProfile('tahchinbot')
    # ip.generate_aggregate_charts()
    # ip.generate_hashtags_charts(max_hashtags=None)
    
    # df = pd.read_csv('./instadata/tahchinbot.csv')
    # df['post_day'] = df['timestamp'].apply(lambda x: pd.Timestamp(x, unit='s', tz='Asia/Tehran').dayofweek)
    # df['post_hour'] = df['timestamp'].apply(lambda x: pd.Timestamp(x, unit='s', tz='Asia/Tehran').hour)
    # df_hour_group = df.groupby(by=['post_hour']).sum()
    # # print(df_hour_group[['likes', 'comments']])
    # df_hour_group[['likes', 'comments']].plot()
    # # plt.bar(x=df_hour_group.index, height=df_hour_group['likes'])
    # # plt.bar(x=df_hour_group.index, height=df_hour_group['comments'])
    # plt.show()

    # print(pd.Timestamp(1555243892, unit='s').dayofweek, pd.Timestamp(1555243892, unit='s', tz='Asia/Tehran').dayofweek)
    # print(pd.Timestamp(1555243892, unit='s').hour, pd.Timestamp(1555243892, unit='s', tz='Asia/Tehran').hour)
