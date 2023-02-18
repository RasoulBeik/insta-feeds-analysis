import re
import os
import nltk
import matplotlib
import matplotlib.cm
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import squarify
import random
from PIL import ImageFont
from nltk import word_tokenize, FreqDist
from bidi.algorithm import get_display
from arabic_reshaper import ArabicReshaper
from hazm import POSTagger
from six import text_type
from wordcloud_generator import WCGenerator

class PersianText:
    def __init__(self, text):
        self.__raw_text__ = text
        self.__result_text__ = text
        self.__all_tokens__ = None
        self.__filtered_tokens__ = None

    def replace(self, find_replace_pairs):
        for pair in find_replace_pairs:
            self.__result_text__ = self.__result_text__.replace(pair[0], pair[1])
        return self

    def reload(self):
        self.__result_text__ = self.__raw_text__

    def tokenize(self, stop_words=None):
        self.__all_tokens__ = word_tokenize(self.__result_text__)
        if stop_words:
            self.__all_tokens__ = [t for t in self.__all_tokens__ if t not in stop_words]
            self.__filtered_tokens__ = self.__all_tokens__.copy()
        return self

    def filter_tokens(self, pos_tags=None, stop_words=None, include_words=None, min_len=1, max_len=100, language=None, reshape=False):
        """
        pos_tags: is a list of tag symbols that should be kept in __tokens__ list.
        tag symbols is based on return value of hazm.POSTagger. for example 'N' means word is a Noun.
        stop_words: is a list of lists of words that should be removed from tokens.
        include_words: is a list of lists of words that tokens should be one of them.
        language: 'fa' for farsi and 'en' for english.
        """
        if self.__all_tokens__ is None:
            self.__all_tokens__ = word_tokenize(self.__result_text__)
            self.__filtered_tokens__ = self.__all_tokens__.copy()
        self.__filtered_tokens__ = [t for t in self.__all_tokens__ if len(t) >= min_len and len(t) <= max_len]

        if include_words is not None:
            # merge all lists in one list
            all_include_words = set([w for words in include_words for w in words])
            self.__filtered_tokens__ = [t for t in self.__filtered_tokens__ if t in all_include_words]

        if stop_words is not None:
            # merge all lists in one list
            all_stop_words = set([w for words in stop_words for w in words])
            self.__filtered_tokens__ = [t for t in self.__filtered_tokens__ if t not in all_stop_words]

        # NOTE: there is a problem in filtering english words! any word with at least one english character is recognized as english!
        if language is not None:
            if language.lower() == 'fa':
                self.__filtered_tokens__ = [t for t in self.__filtered_tokens__ if re.search('[a-zA-Z]', t) is None]
            elif language.lower() == 'en':
                self.__filtered_tokens__ = [t for t in self.__filtered_tokens__ if re.search('[a-zA-Z]', t) is not None]
        if pos_tags is not None:
            tagger = POSTagger(model='resources/postagger.model')
            tag_words = tagger.tag(self.__filtered_tokens__)
            self.__filtered_tokens__ = [w for (w, t) in tag_words if t in pos_tags]

        if reshape == True:
            self.reshape_filtered_tokens()
        return self

    def reshape_filtered_tokens(self):
        reshaper_config = {'language': 'Farsi', 'RIAL SIGN': True}
        reshaper = ArabicReshaper(reshaper_config)
        # reshaped_tokens = [get_display(reshaper.reshape(t)) for t in self.__all_tokens__]
        reshaped_tokens = [reshaper.reshape(t) for t in self.__filtered_tokens__]
        self.__filtered_tokens__ = []
        for x in reshaped_tokens:
            # an exception is raised if get_display can not handle some special characters in token.
            try:
                dx = get_display(x)
                self.__filtered_tokens__.append(dx)
            except AssertionError:
                continue
        return

    @staticmethod
    def reshape(text):
        reshaper_config = {'language': 'Farsi', 'RIAL SIGN': True}
        reshaper = ArabicReshaper(reshaper_config)
        try:
            return get_display(reshaper.reshape(text))
        except:
            return None

    def generate_wordcloud(self, font_path=None, mask=None, background_color='black', repeat=False, scale=1,
                           min_font_size=4, max_font_size=None, max_words=200,
                           colormap=None, contour_width=0, contour_color='black', color_func=None,
                           output_file=None, output_file_sign=None, output_file_text=None,
                           display_online=False):
        """
        generates word cloud based on __filtered_tokens__.
        so this method can be used after filter_tokens method.
        output_file_sign: is a dict for sign text info. its keys are: text, location, font, color.
        output_file_text: is like output_file_sign to write a text in image.
        """
        if self.__filtered_tokens__ is None or len(self.__filtered_tokens__) <= 0:
            return
        
        wordcloud = WCGenerator(words=self.__filtered_tokens__)
        wordcloud.generate(font_path=font_path, mask=mask, background_color=background_color, repeat=repeat, scale=scale,
                 min_font_size=min_font_size, max_font_size=max_font_size, max_words=max_words,
                 colormap=colormap, contour_width=contour_width, contour_color=contour_color, color_func=color_func,
                 output_file=output_file, display_online=display_online)
        if output_file is not None and output_file_sign is not None:
            WCGenerator.draw_text_on_image(output_file,
                                           PersianText.reshape(output_file_sign['text']), output_file_sign['font'],
                                           output_file_sign['location'], output_file_sign['color'])
        if output_file is not None and output_file_text is not None:
            WCGenerator.draw_text_on_image(output_file,
                                           PersianText.reshape(output_file_text['text']), output_file_text['font'],
                                           output_file_text['location'], output_file_text['color'])
        return

    def barchart(self, *args, **kwargs):
        """
        *args: max number of words. if not specified, all words will be considered.
        **kwargs:
            title: title of image
            save_to: image file name
            xlabel, ylabel: label of x and y axes
            width_inch, height_inch: width and height of the result image in inch
            font_name: font path and name of texts on image
        """
        fd = FreqDist(self.__filtered_tokens__)
        if len(args) == 0:
            args = [len(fd)]
        samples = [item for item, _ in fd.most_common(*args)]
        freqs = [fd[sample] for sample in samples]
        if 'linewidth' not in kwargs:
            kwargs['linewidth'] = 2
        title = None
        if 'title' in kwargs:
            title = PersianText.reshape(kwargs['title'])
            del kwargs['title']
        save_to = None
        if 'save_to' in kwargs:
            save_to = kwargs['save_to']
            del kwargs['save_to']
        xlabel = None
        if 'xlabel' in kwargs:
            xlabel = PersianText.reshape(kwargs['xlabel'])
            del kwargs['xlabel']
        ylabel = None
        if 'ylabel' in kwargs:
            ylabel = PersianText.reshape(kwargs['ylabel'])
            del kwargs['ylabel']
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

        font = fm.FontProperties(fname=font_name, size=1.5*width_inch)

        plt.figure(figsize=(width_inch, height_inch))
        plt.bar(range(len(samples)), freqs, **kwargs)
        plt.xticks(range(len(samples)), [text_type(s) for s in samples], rotation=45, fontproperties=font, horizontalalignment='right')
        plt.yticks(fontproperties=font)
        font.set_size(2.5*width_inch)
        plt.title(title, fontproperties=font)
        plt.xlabel(xlabel, fontproperties=font)
        plt.ylabel(ylabel, fontproperties=font)
        plt.tight_layout()
        if save_to is not None:
            plt.savefig(save_to)
        else:
            plt.show()
        plt.close()
        return

    def treemap(self, *args, **kwargs):
        """
        *args: max number of words. if not specified, all words will be considered.
        **kwargs:
            title: title of image
            save_to: image file name
            width_inch, height_inch: width and height of the result image in inch
            font_name: font path and name of texts on image
        """
        fd = FreqDist(self.__filtered_tokens__)
        if len(args) == 0:
            args = [len(fd)]
        samples = [item for item, _ in fd.most_common(*args)]
        freqs = [fd[sample] for sample in samples]
        total = sum(freqs)
        freq_ratios = [freq/total for freq in freqs]
        # freq_ratios_text = ['{}%'.format(ratio*100) for ratio in freq_ratios]

        width_inch = 16
        if 'width_inch' in kwargs:
            width_inch = kwargs['width_inch']
            del kwargs['width_inch']
        height_inch = 10
        if 'height_inch' in kwargs:
            height_inch = kwargs['height_inch']
            del kwargs['height_inch']
        font_name = None
        if 'font_name' in kwargs:
            font_name = kwargs['font_name']
            del kwargs['font_name']
        norm_x = int(100*width_inch)
        norm_y = int(100*height_inch)
        min_font_size = 10
        max_font_size = 150

        plt.figure(figsize=(width_inch, height_inch))
        ax = plt.gca()

        cmap = matplotlib.cm.get_cmap('tab20')
        color = [cmap(random.random()) for i in range(len(freqs))]

        normed = squarify.normalize_sizes(freqs, norm_x, norm_y)
        rects = squarify.padded_squarify(normed, 0, 0, norm_x, norm_y)
        # rects = squarify(normed, 0, 0, norm_x, norm_y)

        x = [rect["x"] for rect in rects]
        y = [rect["y"] for rect in rects]
        dx = [rect["dx"] for rect in rects]
        dy = [rect["dy"] for rect in rects]

        ax.bar(x, dy, width=dx, bottom=y, color=color, label=samples, align="edge")

        va = "top"
        for f, r in zip(freq_ratios, rects):
            x, y, dx, dy = r["x"], r["y"], r["dx"], r["dy"]
            font_size = int(f*max_font_size) if int(f*max_font_size) >= min_font_size else min_font_size
            font = fm.FontProperties(fname=font_name, size=font_size)
            ax.text(x + dx / 2, y + dy / 2, '{}%'.format(round(100*f, 2)), va=va, ha="center", fontproperties=font, alpha=0.7)

        va = "bottom"
        for s, f, r in zip(samples, freq_ratios, rects):
            x, y, dx, dy = r["x"], r["y"], r["dx"], r["dy"]
            font_size = int(f*max_font_size) if int(f*max_font_size) >= min_font_size else min_font_size
            font = fm.FontProperties(fname=font_name, size=font_size)
            ax.text(x + dx / 2, y + dy / 2, s[:15], va=va, ha="center", fontproperties=font, alpha=0.7)

        ax.set_xlim(0, norm_x)
        ax.set_ylim(0, norm_y)

        plt.axis('off')

        title = None
        if 'title' in kwargs:
            title = PersianText.reshape(kwargs['title'])
            del kwargs['title']
        save_to = None
        if 'save_to' in kwargs:
            save_to = kwargs['save_to']
            del kwargs['save_to']

        font = fm.FontProperties(fname=font_name, size=25)
        ax.set_title(title, fontproperties=font)

        if save_to is not None:
            plt.savefig(save_to)
        else:
            plt.show() 
        plt.close()
        return

    def plot(self, *args, **kwargs):
        fd = FreqDist(self.__filtered_tokens__)
        fd.plot(*args, **kwargs)
        return




if __name__ == "__main__":
    pass

    """
    # text = 'green سبز blue آبی آبی red قرمز red سفیدwhite white red123 blackسیاه زرد_نارنجی '
    text = 'نوروز خجسته'
    # with open('./instadata/azarijahromi.caption', 'r') as f:
    #     text = f.read()
    # pt = PersianText(text).replace([('\n', ' '), ('***^^^***', ' ')]).tokenize().filter_tokens(pos_tags=['N'], language='fa', min_len=3, reshape=True)
    stop_words_1 = ['می', 'مي', 'ها']
    stop_words_2 = ['استفاده', 'انجام', 'عکسها']
    include_1 = ['مردم', 'اطلاعات', 'دولت', 'حضور']
    include_2 = ['ایران', 'سفر', 'تلاش', 'اینترنت']
    # with open('./instadata/azarijahromi.caption', 'r') as f:
    #     text = f.read()
    pt = PersianText(text).replace([('_', '-')]).tokenize(). \
         filter_tokens(pos_tags=['N', 'Ne', 'AJ'], stop_words=[stop_words_1, stop_words_2], include_words=None, language='fa', min_len=2, reshape=True)
    import matplotlib
    pt.generate_wordcloud(font_path='./fonts/pixelboy-BZiba.ttf', mask=WCGenerator.circle_mask(500), background_color='white', scale=2, repeat=True,
                          colormap=matplotlib.cm.get_cmap(name='gist_rainbow'), display_online=True, output_file=None, #'./outputs/test-111.png',
                          output_file_sign={'text':'@tagneshan.ir', 'location': 'bottom left', 'color': 'red', 'font': ImageFont.truetype('arial.ttf', size=50)})

    # text = 'ورزشی ۹۷/۱۱/۲۸'
    # print(PersianText.reshape(text))
    """

    # font_path='./fonts/AdobeArabic-Bold.otf'
    font_path = './fonts/B Araz.ttf'

    # text = 'بسی رنج بردم در این سال سی عجم زنده کردم بدین پارسی'
    # text = 'خلیج‌فارس PersianGulf'
    # text = 'لرستان'
    # text = 'نوروزخجسته'
    # text = 'تگ‌نما'
    text = 'تگ‌نشان'
    pt = PersianText(text).tokenize(). \
         filter_tokens(pos_tags=None, stop_words=None, include_words=None, language=None, min_len=2, reshape=True)
    import matplotlib
    pt.generate_wordcloud(font_path=font_path,
                          mask=WCGenerator.image_mask('./images/hashtag-512.png'),
                        #   mask=WCGenerator.image_mask('./images/hashtag-512.png'),
                          background_color='black', scale=1, repeat=True,
                          min_font_size=4, max_font_size=40, max_words=1000,
                          colormap=matplotlib.cm.get_cmap(name='Dark2'),
                        #   color_func=WCGenerator.image_color('./images/charshanbesoori-7.png'),
                        #   color_func=WCGenerator.single_color(color_name='black'),
                          contour_color='darkorange', contour_width=4,
                          display_online=True, output_file='./outputs/tagneshan-icon.png',
                          output_file_sign=None
                        #   output_file_sign={'text':'@tagneshan.ir', 'location': 'bottom left', 'color': 'red', 'font': ImageFont.truetype('arial.ttf', size=50)}
                          )

