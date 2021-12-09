
import cv2
import pytesseract
import re
from pokemon_regex import *

try:
    from PIL import Image
except ImportError:
    import Image

#Invent threshold too big for some japanese letters
def process_image_for_text_on_team_menu(image_section, invert=False):
    im_gray = cv2.cvtColor(image_section, cv2.COLOR_BGR2GRAY)
    thresh = 100
    im_bw = cv2.threshold(im_gray, thresh, 255, cv2.THRESH_BINARY)[1]
    if invert:
        image_section = (255-im_bw)
    return parse_rect_with_pytesseract(image_section, True, True)

def process_image_for_text(image_section, invert=False, support_other_langages=False, psm_7=False):
    im_gray = cv2.cvtColor(image_section, cv2.COLOR_BGR2GRAY)
    thresh = 170
    im_bw = cv2.threshold(im_gray, thresh, 255, cv2.THRESH_BINARY)[1]
    if invert:
        image_section = (255-im_bw)
    return parse_rect_with_pytesseract(image_section, support_other_langages, psm_7)


def process_image_for_element_text(image_section, invert=True):
    im_gray = cv2.cvtColor(image_section, cv2.COLOR_BGR2GRAY)
    thresh = 200
    im_bw = cv2.threshold(im_gray, thresh, 255, cv2.THRESH_BINARY)[1]
    if invert:
        image_section = (255-im_bw)
    return parse_rect_with_pytesseract(image_section, False, True)

def process_image_for_speed_stats_text(image_section, invert=True):
    img_adj = image_section.copy()
    lower =(0, 0, 0) # lower bound for each channel
    upper = (180, 180, 180) # upper bound for each channel

    # create the mask and use it to change the colors
    mask = cv2.inRange(img_adj, lower, upper)
    masked_color = [255,255,255]
    mask = 255 - mask
    img_adj[mask != 0] = masked_color
    #cv2_imshow(img_adj)

    lower =(0, 0, 0) # lower bound for each channel
    upper = (70, 70, 70) # upper bound for each channel

    # create the mask and use it to change the colors
    mask = cv2.inRange(img_adj, lower, upper)
    masked_color = [15,15,15]
    mask = 255 - mask
    img_adj[mask != 255] = masked_color
    #cv2_imshow(img_adj)

    return parse_rect_with_pytesseract(img_adj, False, True)

def process_image_for_element_text2(image_section, invert=True):
    im_gray = cv2.cvtColor(image_section, cv2.COLOR_BGR2GRAY)
    thresh = 127
    im_bw = cv2.threshold(im_gray, thresh, 255, cv2.THRESH_BINARY)[1]
    if invert:
        image_section = (255-im_gray)
    return image_section

def calculate_communicating_black_ratio(image):
    return calculate_health_ratio(image)

def calculate_health_ratio(image):
    # make non grey pixels yellow
    img_adj = image.copy()
    lower =(0, 0, 0) # lower bound for each channel
    upper = (140, 140, 140) # upper bound for each channel

    # create the mask and use it to change the colors
    mask = cv2.inRange(img_adj, lower, upper)
    masked_color = [0,255,255]
    mask = 255 - mask
    img_adj[mask != 0] = masked_color
    return count_non_yellow_pixels(img_adj, masked_color)

def count_non_yellow_pixels(image, mask):
    # grab the image dimensions
    h = image.shape[0]
    w = image.shape[1]
    target_pixels = 0


    # loop over the image, pixel by pixel
    for y in range(0, h):
        for x in range(0, w):
          pixel = image[y, x]
          if pixel[0] == mask[0] and pixel[1] == mask[1] and pixel[2] == mask[2]:
            target_pixels += 1
    return target_pixels / float(h*w)

def apply_filter_for_gender_removal(image_section):
    # load image and set the bounds
    img = image_section.copy()
    lower =(0, 0, 0) # lower bound for each channel
    upper = (140, 140, 140) # upper bound for each channel

    # create the mask and use it to change the colors
    mask = cv2.inRange(img, lower, upper)
    mask = 255 - mask
    img[mask != 0] = [255,255,255]

    # Make black and white

    return img

def get_active_name(image_section):
    img = Image.fromarray(apply_filter_for_gender_removal(image_section))
    text = pytesseract.image_to_string(img, lang="jpn+kor+chi-sim+chi-tra")
    return text

def parse_active_name_with_pytesseract(image_section):
    result = parse_rect_with_pytesseract(image_section)
    if re.search(pokemon_names_regex, result):
        result = re.search(pokemon_names_regex, result).group(0)
    return result

# Currently 1 usage to know when to click the message for showing nicknames
def parse_network_message(image_section):
    result = parse_rect_with_pytesseract(image_section)
    return result

#FOreign languages used on
#Used on team preview
#Used with messages
def parse_rect_with_pytesseract(image_section, support_other_langages=False, psm_7=False):
    img = Image.fromarray(image_section)
    if support_other_langages and psm_7:
        raw_text = pytesseract.image_to_string(img, lang="jpn+kor+chi-sim", config='--psm 7')
    elif support_other_langages:
        raw_text = pytesseract.image_to_string(img, lang="jpn+kor+chi-sim")
    elif psm_7:
        raw_text = pytesseract.image_to_string(img, config='--psm 7')
    else:
        raw_text = pytesseract.image_to_string(img, lang="eng")
    raw_text = raw_text.replace('’', '\'')
    raw_text = raw_text.replace('|', 'I')
    raw_text = raw_text.replace('\n', ' ')
    # handle both cases of galar champ
    raw_text = raw_text.replace('the Galar Championl', '')
    raw_text = raw_text.replace('the Galar Champion', '')
    raw_text = raw_text.strip()
    raw_text = convert_non_ascii_string(raw_text)
    return raw_text

def convert_non_ascii_string(input_string):
    if len(input_string) < 3:
        return input_string
    new_string = input_string[0]
    for i in range(1, len(input_string)-1):
        prev = input_string[i-1]
        curr = input_string[i]
        next_str = input_string[i+1]

        if curr == ' ' and (not is_ascii(prev) and not is_ascii(next_str)):
            continue

        new_string += curr

    curr = input_string[-1]
    new_string += curr
    return new_string


def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def get_last_number_or_neg(number):
    if re.search(last_number_regex, number):
        return int(re.search(last_number_regex, number).group())
    return -1

def get_first_number_or_neg(number):
    if re.search(first_number_regex, number):
        return int(re.search(first_number_regex, number).group())
    return -1


# Returns true if edit distance between s1 and s2 is
# one, else false
def isEditDistanceWithinTwo(s1, s2, max_mistakes = 2):
#    if s1 == None and s2 == None:
#        return True
    if s1 == None or s2 == None:
        return False

    # Find lengths of given strings
    m = len(s1)
    n = len(s2)

    # If difference between lengths is more than 1,
    # then strings can't be at one distance
    if abs(m - n) > max_mistakes:
        return False

    count = 0    # Count of isEditDistanceOne

    i = 0
    j = 0
    while i < m and j < n:
        # If current characters dont match
        if s1[i] != s2[j]:
            if count == max_mistakes:
                return False

            # If length of one string is
            # more, then only possible edit
            # is to remove a character
            if m > n:
                i+=1
            elif m < n:
                j+=1
            else:    # If lengths of both strings is same
                i+=1
                j+=1

            # Increment count of edits
            count+=1

        else:    # if current characters match
            i+=1
            j+=1

    # if last character is extra in any string
    if i < m or j < n:
        count+=1

    return count <= max_mistakes
