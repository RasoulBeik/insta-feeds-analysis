from PIL import Image, ImageDraw, ImageFont
from persiantext import PersianText

class Text2Image:
    def __init__(self, text, image_size=(1000, 1000), margin=30, line_space=10, background_color='white'):
        self.__margin__ = margin
        self.__image__ = Image.new(mode='RGBA', size=image_size, color=background_color)

        ypos = margin

        # line format font_file;font_size;color;align;text
        lines = text.split('\n')
        for line in lines:
            if line.strip():
                line_parts = line.split(';')
                ypos = line_space + \
                    self.__draw_string__(string=line_parts[4], ypos=ypos, \
                                            font_file=line_parts[0], font_size=int(line_parts[1]), \
                                            color=line_parts[2], align=line_parts[3])
            else:
                ypos = ypos + line_space

        return

    def show(self):
        self.__image__.show()
        return

    def save(self, result_file):
        self.__image__.save(result_file)
        return

    def __draw_string__(self, string, ypos, font_file, font_size=20, color='black', align='right'):
        font = ImageFont.truetype(font=font_file, size=font_size)
        string = PersianText.reshape(string)
        string_size = font.getsize(string)
        
        # crop string to fit in image width
        while string_size[0] > self.__image__.width - 2*self.__margin__:
            string = string[1:]
            string_size = font.getsize(string)

        if align.lower() == 'left':
            xpos = self.__margin__
        elif align.lower() == 'center':
            xpos = self.__image__.width // 2 - string_size[0] // 2
        elif align.lower() == 'right':
            xpos = self.__image__.width - string_size[0] - self.__margin__
        draw = ImageDraw.Draw(self.__image__)
        draw.text((xpos, ypos), string, font=font, fill=color)
        return ypos + string_size[1]

if __name__ == "__main__":
    pass

    # with open('./outputs/report.txt') as f:
    #     text = f.read()
    # ti = Text2Image(text, image_size=(1000, 1200))
    # ti.__draw_string__('This is a test', 50, font_file='arialbd.ttf', font_size=30, color='black', align='left')
    # ti.__draw_string__('This is a test', 50, font_file='Impact.ttf', font_size=30, color=(100, 150, 200), align='center')
    # ti.__draw_string__('This is a test', 50, font_file='arialbd.ttf', font_size=30, color='black', align='right')

    # ti.__draw_string__('این یک تست است.', 150, font_file='Iranian Sans.ttf', font_size=30, color='black', align='left')
    # ti.__draw_string__('این یک تست است.', 180, font_file='EntezarD6_v2.0.1.ttf', font_size=30, color=(100, 150, 200), align='center')
    # ti.__draw_string__('این یک تست است.', 210, font_file='pixelboy-BJadidBold.ttf', font_size=30, color='black', align='right')
    # ti.save('./outputs/report.png')


#     text = """
# ./fonts/B Araz.ttf;65;red;center;آیا می‌دانید ...
# EntezarD6_v2.0.1.ttf;180;green;center;ضریب تعامل
# ./fonts/B Araz.ttf;55;blue;center;در اینستاگرام چیست؟
# ./fonts/B Araz.ttf;65;blue;center;ضریب تعامل معیاری است که میزان مشارکت مخاطبان را
# ./fonts/B Araz.ttf;65;blue;center;در لایک کردن و کامنت گذاری روی پست‌ها نشان می‌دهد.
# ./fonts/B Araz.ttf;65;blue;center;هرچه ضریب تعامل یک صفحه بزرگتر باشد،
# ./fonts/B Araz.ttf;65;blue;center;به این معنی است که پست‌ها بیشتر مورد توجه قرار گرفته‌اند.
# arialbd.ttf;40;red;center;@tagneshan.ir
#     """

#     text = """
# ./fonts/B Araz.ttf;100;darkblue;center;با
# EntezarD6_v2.0.1.ttf;240;red;center;تگ نشان
# ./fonts/B Araz.ttf;100;darkblue;center;از ضریب تعامل صفحه خود
# ./fonts/B Araz.ttf;100;darkblue;center;آگاه شوید و با چشم باز
# ./fonts/B Araz.ttf;100;darkblue;center;برای بهبود آن برنامه‌ریزی کنید.
# arialbd.ttf;60;red;center;@tagneshan.ir
#     """
#     text = """
# ./fonts/B Araz.ttf;70;blue;center;با
# EntezarD6_v2.0.1.ttf;150;green;center;تگ نشان
# ./fonts/B Araz.ttf;70;blue;center;صفحه اینستاگرام خود را
# ./fonts/B Araz.ttf;300;darkred;center;رایگان
# ./fonts/B Araz.ttf;70;blue;center;تحلیل کنید.
# ./fonts/B Araz.ttf;70;blue;center;ورق بزنید ...
# arialbd.ttf;30;red;center;@tagneshan.ir
#     """

#     text = """
# ./fonts/B Araz.ttf;70;blue;center;شرایط تحلیل رایگان صفحه اینستاگرام
# ./fonts/B Araz.ttf;70;blue;right;۱- بیش از پنج هزار فالوور داشته باشید.
# ./fonts/B Araz.ttf;70;blue;right;۲- بیش از صد پست داشته باشید.
# ./fonts/B Araz.ttf;70;blue;right;۳- از هشتگ در متن پست‌ها استفاده کرده باشید.
# ./fonts/B Araz.ttf;80;green;center;تحلیل رایگان برای پنج نفر اولی است که
# ./fonts/B Araz.ttf;80;green;center;دایرکت پیام دهند.
# arialbd.ttf;30;red;center;@tagneshan.ir
#     """

#     text = """
# ./fonts/B Araz.ttf;70;red;center;آیا می‌دانید ...
# ./fonts/B Araz.ttf;65;green;center;هشتگ‌هایی که در پست‌ها بکار می‌برید، بر میزان کامنت‌ها موثر است؟
# EntezarD6_v2.0.1.ttf;220;red;center;تگ نشان
# ./fonts/B Araz.ttf;65;green;center;تعداد کامنت به ازای هشتگ‌ها را نمایش می‌دهد.
# arialbd.ttf;40;red;center;@tagneshan.ir
#     """

#     text = """
# ./fonts/B Araz.ttf;70;red;center;فالوئر زیاد به تنهایی کافی نیست!
# ./fonts/B Araz.ttf;65;green;center;با آگاهی از
# EntezarD6_v2.0.1.ttf;120;green;center;ضریب تعامل
# ./fonts/B Araz.ttf;65;green;center;از میزان محبوبیت پست‌های خود آگاه شوید.
# Entezar2_v2.0.1.ttf;60;red;center;تگ نشان
# arialbd.ttf;30;red;center;@tagneshan.ir
#     """

    text = """
./fonts/B Araz.ttf;80;darkred;center;روش‌های ارتقای هشتگ برند




Entezar2_v2.0.1.ttf;30;darkorange;center;تگ نشان
arialbd.ttf;20;darkorange;center;@tagneshan
arialbd.ttf;20;darkorange;center;http://tagneshan.rooznema.ir
    """

#     text = """
# impact.ttf;600;black;center;AX
#     """

    Text2Image(text, image_size=(610, 250), line_space=10, margin=20, background_color=(255,255,255,0)) \
        .save('/home/rasoul/apps/tagneshan/posts/temp.png')
    pass