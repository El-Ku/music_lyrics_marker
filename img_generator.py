from PIL import Image, ImageFont, ImageDraw  
import math
import os 
import time

class ImgGenerator():
    def __init__(self, draw_gui_object):
        self.im_w = 1920
        self.im_h = 1080
        self.cwd = os.getcwd()
        self.font_name_dn = r'C:\Users\wipin\OneDrive\Python\env\Learning_Python\KYV_video_generation\fonts\TiroDevanagariSanskrit-Regular.ttf'
        self.font_name_en = r'C:\Users\wipin\OneDrive\Python\env\Learning_Python\KYV_video_generation\fonts\NotoSans-VariableFont_wdth_wght.ttf'
        self.font_color = '#271300'
        self.heading_h = 100  # pixels
        self.dn_h = math.floor((self.im_h-self.heading_h)*0.7)
        self.iast_h = self.im_h - self.heading_h - self.dn_h
        self.start_left_pos = 40
        self.avlble_width = self.im_w - 2*self.start_left_pos
        self.gap_between_lines_dn = 8  # pixels
        self.gap_between_lines_en = 4  # pixels
        self.stop_img_creation_flag = False  
        self.img_generation_under_progress = False
        self.find_heights_lang()
        self.draw_gui_class = draw_gui_object

    def find_heights_of_fontsizes(self, max_font_size, sample_text, font_name):
        font_size = 0
        font_heights = []
        while(font_size <= max_font_size):
            font_size += 1
            font = ImageFont.truetype(font_name,font_size)
            text_box_size = font.getbbox(sample_text)
            font_heights.append(text_box_size[3]-text_box_size[1])
        # print(font_heights)
        return font_heights

    def find_heights_lang(self):
        # get approximate font heights for font sizes from 1 to 100 for a sample text.
        self.font_heights_dn = self.find_heights_of_fontsizes(max_font_size=100, \
            sample_text="शुंध॑ध्वं॒ दैव्या॑य॒ कर्म॑णे देवय॒ज्यायै॑ मात॒रिश्व॑नो  घ॒र्मो॑ऽसि॒ द्यौर॑सि पृथि॒व्य॑सि वि॒श्वधा॑या असि पर॒मेण॒ धाम्ना॒  दृꣳह॑स्व॒ मा ह्वा॒र्वसू॑नाम्प॒वित्र॑मसि श॒तधा॑रं॒", \
            font_name = self.font_name_dn)
        self.font_heights_en = self.find_heights_of_fontsizes(max_font_size=100, \
            sample_text="śuṃdha̍dhva̱ṃ daivyā̍ya̱ karma̍ṇe devaya̱jyāyai̍ māta̱riśva̍no  gha̱rmo̎si̱ dyaura̍si pṛthi̱vya̍si vi̱śvadhā̍yā asi para̱meṇa̱ dhāmnā̱ dṛgͫha̍sva̱", \
            font_name = self.font_name_en)
        
    def get_font_size(self, mode, single_line, avlble_h, min_font_size=16):
        if(mode == "dn"): #devanagari
            font_name = self.font_name_dn
            font_heights = self.font_heights_dn
            gap_between_lines = self.gap_between_lines_dn
        else:  #iast
            font_name = self.font_name_en
            font_heights = self.font_heights_en
            gap_between_lines = self.gap_between_lines_en   

        font_size = min_font_size
        while(font_size <= 100):
            font = ImageFont.truetype(font_name,font_size)
            text_len = font.getlength(single_line)
            min_num_lines = math.ceil(float(text_len) / self.avlble_width)
            # print(font_size,text_len,min_num_lines,(font_heights[font_size]+gap_between_lines) * min_num_lines)
            # return the font_size when it uses more than 90% of available space
            if((font_heights[font_size]+gap_between_lines) * min_num_lines > avlble_h*0.9):  
                return font_size-1 
            else:
                font_size += 1
        return font_size-1  # font_size is 100 in this case

    def single2multi_lines(self, words, draw_bg, font):
        resultTextLength = 0
        result_text = ""
        messageBreakLineIndexes = []
        # Iterate over the words directly as an iterable, not by len
        for word in words:
            # Check the width of the current line plus the next word
            word_width = draw_bg.textlength(word, font=font)
            if resultTextLength + word_width <= self.avlble_width:
                # If the line isn't too wide, add the word to the line
                result_text += word + " "
                resultTextLength += word_width + draw_bg.textlength(" ", font=font)  # Add space width
            else:
                # If the line is too wide, break the line
                result_text = result_text.rstrip() + "\n"
                messageBreakLineIndexes.append(len(result_text))
                result_text += word + " "
                resultTextLength = word_width + draw_bg.textlength(" ", font=font)  # Reset line width
        return  messageBreakLineIndexes, result_text

    def get_multi_lines(self, mode, single_line, avlble_h, draw_bg, min_font_size=16):
        if(mode == "dn"): #devanagari
            font_name = self.font_name_dn
            gap_between_lines = self.gap_between_lines_dn
        else:  #iast
            font_name = self.font_name_en
            gap_between_lines = self.gap_between_lines_en

        font_size = self.get_font_size(mode, single_line, avlble_h, min_font_size)
        font = ImageFont.truetype(font_name,font_size)
        words = single_line.split()
        while(True):
            messageBreakLineIndexes, result_text = self.single2multi_lines(words, draw_bg, font)
            for i in range(len(messageBreakLineIndexes)):
                index = messageBreakLineIndexes[i]
                result_text = result_text[:index+i] + "\n" + result_text[index+i:]
            text_box_size = draw_bg.multiline_textbbox((self.start_left_pos,0), result_text, font, spacing=gap_between_lines)
            # print("text_box_size=", text_box_size,"max_avalble_h=",avlble_h-30,"font_size=",font_size)
            if(text_box_size[3] < avlble_h-30):
                break
            # the text box size is bigger than its supposed to be. 
            # decrement fontsize and try again
            else:  
                font_size -= 1
                font = ImageFont.truetype(font_name,font_size)
        return result_text, font, font_size, len(messageBreakLineIndexes)+1

    def create_single_img(self, dn_l,iast_l,head_l,file_num):
        
        bg_image_handle = Image.open("other_files\\blank.jpg")
        bg_image_handle = bg_image_handle.resize((self.im_w, self.im_h))

        # draw the background image
        draw_bg = ImageDraw.Draw(bg_image_handle)

        # add heading text to the image
        font = ImageFont.truetype(self.font_name_dn, 32)
        draw_bg.text((self.im_w/2, 40), head_l, font=font, fill=self.font_color, anchor='mm')  

        # convert single line to multi lines and add devangari text to the image
        multi_line_dn, font_dn, font_size_dn, num_lines = self.get_multi_lines("dn", dn_l, self.dn_h, draw_bg, min_font_size=10)
        # print("num_lines(dn)=",num_lines)
        if(num_lines == 1):  # single line of lyrics
            draw_bg.text((self.start_left_pos, self.im_h*0.3), multi_line_dn, font=font_dn, fill=self.font_color, spacing=self.gap_between_lines_dn)  
            # find out the actual size, the dn text has occupied
            text_box_size = draw_bg.multiline_textbbox((self.start_left_pos, self.im_h*0.3),multi_line_dn,font_dn, spacing=self.gap_between_lines_dn)  
            en_h = self.im_h*0.25
        else:    
            draw_bg.text((self.start_left_pos, self.heading_h+20), multi_line_dn, font=font_dn, fill=self.font_color, spacing=self.gap_between_lines_dn)  
            # find out the actual size, the dn text has occupied
            text_box_size = draw_bg.multiline_textbbox((self.start_left_pos, self.heading_h+20),multi_line_dn,font_dn, spacing=self.gap_between_lines_dn)  
            en_h = self.im_h-text_box_size[3]-10
    
        # convert single line iast into multi line iast
        multi_line_en, font_en, font_size_en, num_lines = self.get_multi_lines("en", iast_l, en_h, draw_bg, min_font_size=10)
        # print("num_lines(en)=",num_lines)

        # add the iast text to image after adjusting the font size.
        if(font_size_en > font_size_dn):
            font_size_en = self.font_heights_dn
            font_en = ImageFont.truetype(self.font_name_en, font_size_en)

        if(num_lines == 1):
            draw_bg.text((self.start_left_pos, text_box_size[3]+200), multi_line_en, font=font_en, fill=self.font_color, spacing=self.gap_between_lines_en)   
        else:
            draw_bg.text((self.start_left_pos, text_box_size[3]+30), multi_line_en, font=font_en, fill=self.font_color, spacing=self.gap_between_lines_en)  

        # save the final image to disk
        bg_image_handle.save("lyric_images\\" + str(file_num) + ".png")
        
    def generate_images(self):
        self.img_generation_under_progress = True
        dn_lyrics = []
        en_lyrics = []
        head_lyrics = []
        # read the text files and gather what needs to be printed on the images
        with open('other_files\devanagari.txt', 'r', encoding='utf-8') as file:
            for line in file:
                dn_lyrics.append(line)
        with open('other_files\iast.txt', 'r', encoding='utf-8') as file:
            for line in file:
                en_lyrics.append(line)
        with open('other_files\heading.txt', 'r', encoding='utf-8') as file:
            for line in file:
                head_lyrics.append(line)
        print("Number of lines to create images for = ",len(dn_lyrics))
        assert len(dn_lyrics) == len(en_lyrics), "dn and en have different sizes. Check lyrics.py file"
        assert len(dn_lyrics) == len(head_lyrics), "dn and head have different sizes. Check lyrics.py file"
        print("Sanity test: lyrics and heading text files have same sizes")
        
        start_time_secs = time.time()
        for ind in range(len(dn_lyrics)):
            self.draw_gui_class.update_time_boxes_img_vid_gen(len(dn_lyrics), ind, time.time()-start_time_secs)
            if(self.stop_img_creation_flag == True):
                print("Stopped image creation midway")
                self.stop_img_creation_flag = False
                break
            dn_l = dn_lyrics[ind]
            en_l = en_lyrics[ind]
            head_l = head_lyrics[ind]
            self.create_single_img(dn_l, en_l, head_l, ind+1)
            print("Created image for line#", ind+1)
        print(f"It took {time.time()-start_time_secs} seconds to finish processing {ind+1} images")
        self.img_generation_under_progress = False
        self.draw_gui_class.update_time_boxes_img_vid_gen(len(dn_lyrics), ind, time.time()-start_time_secs)
        
    def stop_img_creation(self):
        if(self.img_generation_under_progress == True):
            self.stop_img_creation_flag = True   
            print("Stop image generation button was pressed")