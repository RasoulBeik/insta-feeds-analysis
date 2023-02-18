import numpy as np
from PIL import Image, ImageEnhance, ImageFont, ImageDraw
from wordcloud import WordCloud, ImageColorGenerator
import nltk
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime
import datetimeutil
import os

###### class WCGenerator ######
class WCGenerator:
    def __init__(self, words=None, from_file=None):
        self.__words__ = words
        # if both words and from_file are not None, file content overwrites words.
        if from_file is not None:
            with open(from_file, 'r') as f:
                content = f.read()
                self.__words__ = content.split(' ')
        return

    ###### generates world cloud from array of words ######
    def generate(self, font_path=None, mask=None, background_color='black', repeat=False, scale=1,
                 min_font_size=4, max_font_size=None, max_words=200,
                 colormap=None, contour_width=0, contour_color='black', color_func=None,
                 output_file=None, display_online=False):
        if self.__words__ is None:
            return

        wcloud = WordCloud(font_path=font_path, scale=scale, background_color=background_color, mask=mask,
                           min_font_size=min_font_size, max_font_size=max_font_size, max_words=max_words, repeat=repeat,
                           colormap=colormap, contour_width=contour_width, contour_color=contour_color, color_func=color_func)

        # __words__ can be a list or a string
        if isinstance(self.__words__, list):
            frequent_dist = nltk.FreqDist(self.__words__)
            wcloud = wcloud.generate_from_frequencies(frequent_dist)
        else:
            wcloud = wcloud.generate(self.__words__)

        if output_file is not None:
            wcloud.to_file(output_file)
        if display_online:
            plt.figure(figsize=(12, 12))
            plt.imshow(wcloud, interpolation='bilinear')
            plt.axis('off')
            plt.show()
        return

    def generate_2(self, font_path=None, mask=None, background_color='black', repeat=False, scale=1,
                 colormap=None, contour_width=0, contour_color='black', color_func=None,
                 output_file=None, display_online=False):
        if self.__words__ is None:
            return

        frequent_dist = nltk.FreqDist(self.__words__)

        wcloud = WordCloud(font_path=font_path, scale=scale, background_color=background_color, mask=mask,
                           colormap=colormap, contour_width=contour_width, contour_color=contour_color, color_func=color_func)
        wcloud = wcloud.generate_from_frequencies(frequent_dist)
        if output_file is not None:
            wcloud.to_file(output_file)
        if display_online:
            plt.figure(figsize=(12, 12))
            plt.imshow(wcloud, interpolation='bilinear')
            plt.axis('off')
            plt.show()
        return

    # generates dotted colored image (snowy image) from original image.
    @staticmethod
    def generate_colored_image(input_image_file, output_image_file, input_enhance_factor=1, output_enhance_factor=1, max_words=200000):
        wcloud = WordCloud(scale=1, background_color='white',
                        mask=WCGenerator.image_mask(input_image_file),
                        color_func=WCGenerator.image_color(input_image_file, enhance_factor=input_enhance_factor),
                        max_font_size=4, max_words=max_words, repeat=True)
        
        # generates word cloud and convert it to numpy array.
        # 'xx' is repeated to generate word cloud. WordCloud class does not allow single character as a word!
        np_image = wcloud.generate('xx').to_array()

        # creates image from numpy array, then enhances and saves it to out file.
        image = Image.fromarray(np_image)
        enhancer = ImageEnhance.Contrast(image)
        enhancer.enhance(output_enhance_factor).save(output_image_file)
        return

    @staticmethod
    def circle_mask(size):
        x, y = np.ogrid[:size, :size]
        mask = (x - size/2) ** 2 + (y - size/2) ** 2 > (size/2 - 0.1*size) ** 2
        mask = 255 * mask.astype(int)
        return mask
        
    @staticmethod
    def image_mask(filepath):
        mask = np.array(Image.open(filepath))
        return mask

    # generate colors based on colors of an image file. it is used as color_func parameter of WordCloud.
    @staticmethod
    def image_color(filepath, enhance_factor=1):
        # image = np.array(Image.open(filepath))
        # return ImageColorGenerator(image)
        image = Image.open(filepath)
        enhancer = ImageEnhance.Contrast(image)
        enhanced_image = enhancer.enhance(enhance_factor)
        np_image = np.array(enhanced_image)
        return ImageColorGenerator(np_image)

    # generate single color based on name or RGB. it is used as color_func parameter of WordCloud.
    @staticmethod
    def single_color(color_name=None, rgb=(0, 0, 0)):
        if color_name is not None:
            return lambda *args, **kwargs: color_name
        return lambda *args, **kwargs: rgb

    ###### function generate output file name for word cloud ######
    @staticmethod
    def generate_output_filename(path):
        # generating output file name based on current timestamp
        ts = datetime.now().timestamp()
        fn = datetimeutil.timestamp_to_date_str(ts, str_format='%Y%m%d-')+str(int(ts))
        slash = '' if path[-1] == '/' else '/'
        output_file = '{}{}{}.png'.format(path, slash, fn)
        return output_file

    @staticmethod
    def enhance_image(image_path, enhance_factor=1):
        x = os.path.splitext(image_path)
        new_image_path = '{}-{}{}'.format(x[0], str(enhance_factor), x[1])
        img = Image.open(image_path)
        enhancer = ImageEnhance.Contrast(img)
        enhancer.enhance(enhance_factor).save(new_image_path)
        return

    @staticmethod
    def draw_text_on_image(image_path, text, font, location='top left', color=None):
        """
        location: 'top left', 'top center', 'top right',
                'middle left', 'middle center', 'middle right',
                'right left', 'right center', 'right right'
                OR (x, y) coordination of text on image
        """
        margin = 30
        text_size = font.getsize(text)
        img = Image.open(image_path).convert("RGBA")

        x, y = margin, margin
        coord = (x, y)
        if isinstance(location, str):
            location = location.lower()
            if location.find('top') >= 0:
                y = margin
                if location.find('left') >= 0:
                    x = margin
                elif location.find('right') >= 0:
                    x = img.width - text_size[0] - margin
                elif location.find('center') >= 0:
                    x = img.width // 2 - text_size[0] // 2
            elif location.find('middle') >= 0:
                y = img.height // 2 - text_size[1] //2
                if location.find('left') >= 0:
                    x = margin
                elif location.find('right') >= 0:
                    x = img.width - text_size[0] - margin
                elif location.find('center') >= 0:
                    x = img.width // 2 - text_size[0] // 2
            elif location.find('bottom') >= 0:
                y = img.height - text_size[1] - margin
                if location.find('left') >= 0:
                    x = margin
                elif location.find('right') >= 0:
                    x = img.width - text_size[0] - margin
                elif location.find('center') >= 0:
                    x = img.width // 2 - text_size[0] // 2
            coord = (x, y)
        elif isinstance(location, tuple):
            coord = location
        draw = ImageDraw.Draw(img)
        draw.text(coord, text, font=font, fill=color)
        img.save(image_path)
        return


# this section is just for test!
if __name__ == "__main__":
    pass
    # WCGenerator(from_file='./outputs/sports-20190203-1549195691.png.tags'). \
    #     generate(font_path='./fonts/pixelboy-BZiba.ttf', display_online=True, mask=WCGenerator.image_mask('./images/ball-1.png'),
    #             contour_color='green', contour_width=2, colormap=matplotlib.cm.gist_rainbow)

    # WCGenerator(from_file='./outputs/cinema-20190203-1549180466.png.tags'). \
    #     generate(font_path='./fonts/pixelboy-BZiba.ttf', display_online=True, mask=WCGenerator.image_mask('./images/camera-1.png'),
    #             contour_color='green', contour_width=5, colormap=matplotlib.cm.gist_rainbow, repeat=True, background_color='black')

    # WCGenerator(from_file='./outputs/cinema-20190203-1549180466.png.tags'). \
    #     generate(font_path='./fonts/pixelboy-BZiba.ttf', display_online=True,
    #              mask=WCGenerator.image_mask('./images/man-1.png'),
    #              color_func=WCGenerator.image_color('./images/man-1.png'),
    #              contour_color='green', contour_width=0, repeat=True, background_color='white', scale=3)

    # WCGenerator(from_file='./outputs/cinema-20190203-1549180466.png.tags'). \
    #     generate(font_path='./fonts/pixelboy-BZiba.ttf', display_online=True,
    #              mask=WCGenerator.circle_mask(500),
    #              color_func=WCGenerator.single_color('black'),
    #              contour_color='green', contour_width=0, repeat=True, background_color='white', scale=3)

    # WCGenerator(['.']). \
    #     generate(#font_path='./fonts/pixelboy-BZiba.ttf',
    #              display_online=True,
    #              mask=WCGenerator.circle_mask(500),
    #              color_func=WCGenerator.single_color('black'),
    #              contour_color='green', contour_width=0, repeat=True, background_color='white', scale=3)

    # wcloud = WordCloud(scale=1, background_color='white',
    #                    mask=WCGenerator.image_mask('./images/taba-1.jpg'),
    #                    color_func=WCGenerator.image_color('./images/taba-1.jpg', enhance_factor=5),
    #                    contour_width=0, contour_color='black',
    #                    max_font_size=4, max_words=200000,
    #                    repeat=True)
    # wcloud = wcloud.generate('xx').to_file('./outputs/taba-1.png')
    # plt.figure(figsize=(12, 12))
    # plt.imshow(wcloud, interpolation='bilinear')
    # plt.axis('off')
    # plt.show()
    
    # im = Image.open('./outputs/nazy_kh-Btnbcr3nt25.png')
    # enhancer = ImageEnhance.Contrast(im)
    # enhancer.enhance(3).save('./outputs/nazy_kh-Btnbcr3nt25-3.png')

    # fn = 'bijan_banafshehkhah-Bm9NkEcFBsF'
    # input_file = './images/{}.jpg'.format(fn)
    # output_file = './outputs/{}.png'.format(fn)
    # WCGenerator.generate_colored_image(input_file, output_file, input_enhance_factor=5, output_enhance_factor=1, max_words=500000)
    # WCGenerator.enhance_image(output_file, enhance_factor=2)
    # WCGenerator.enhance_image(output_file, enhance_factor=3)

    # font = ImageFont.truetype('./fonts/pixelboy-BZiba.ttf', size=70)
    # font = ImageFont.truetype('arial.ttf', size=100)
    # WCGenerator.draw_text_on_image('./outputs/20190213-1550030994-2.png', 'left', font=font, location='bottom left', color='blue')
    # WCGenerator.draw_text_on_image('./outputs/20190213-1550030994-2.png', 'رررررررراست', font=font, location='bottom right', color='blue')
    # WCGenerator.draw_text_on_image('./outputs/20190213-1550030994-2.png', 'QWERTYUIOPASDF', font=font, location=(500, 800), color='yellow')

    WCGenerator(words='نوروز خجسته') \
                .generate(font_path='./fonts/pixelboy-BZiba.ttf',
                          mask=WCGenerator.circle_mask(800),
                        #   mask=WCGenerator.image_mask(mask_images_path+'frame-8.png'),
                          colormap=matplotlib.cm.get_cmap('gist_rainbow'),
                        #   color_func=WCGenerator.single_color('black'),
                          output_file=None,
                          display_online=True, contour_color='brown', contour_width=0, scale=2, repeat=True,
                          background_color='black')
