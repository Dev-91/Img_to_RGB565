import argparse
import os
import cv2
from PIL import Image
from enum import Enum

class Mode(Enum):
    H = ".h"
    PNG = ".png"
    GIF = ".gif"

def main():
    parser = argparse.ArgumentParser(
        description="Convert a file from one format to another."
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        dest="input_file",
        help="Input file to be converted."
    )
    parser.add_argument(
        "-o",
        "--output",
        nargs="?",
        dest="output_file",
        help="Output file to be converted."
    )
    parser.add_argument(
        "-r",
        "--resize",
        dest="resize",
        help="Resize image."
    )
    parser.add_argument(
        "-d",
        "--delete",
        dest="delete_temp",
        help="Delete temp image."
    )
    parser.add_argument(
        "-s",
        "--swap",
        dest="swap",
        help="Swap bytes for 16-bit words."
    )
    args = parser.parse_args()

    input_basename = os.path.basename(args.input_file).rsplit('.', 1)

    mode = Mode.H if (input_basename[1] == 'png') else Mode.PNG

    if args.output_file is None:
        args.output_file = input_basename[0] + mode.value

    output_basename = os.path.basename(args.output_file).rsplit('.', 1)

    if len(output_basename) != 2:
        print("Error: Invalid arguments.")
        exit(1)

    if (input_basename[1] not in ['gif', 'png', 'h']):
        print("Error: Input file must be a gif or .png or .h file.")
        exit(1)

    if (output_basename[1] not in ['png', 'h']):
        print("Error: Output file must be a png or .h file.")
        print(f"Output file: {output_basename}")
        exit(1)

    if (input_basename[1] == output_basename[1]):
        print("Error: Input and output file must be different.")
        exit(1)

    if input_basename[1] == 'gif':
        target_path_list = []
        temp_img_list = convert_gif_to_png(args)
        for img in temp_img_list:
            target_path_list.append(resize_img(img, args.resize))
        convert_gif_to_rgb565(args, target_path_list)
        print_image_info("Convert Image ", target_path_list[0])
        delete_temp(args)
    elif input_basename[1] == 'png':
        target_path = resize_img(args.input_file, args.resize)
        convert_png_to_rgb565(args, target_path)
        print_image_info("Convert Image ", target_path)
        delete_temp(args)
    elif input_basename[1] == 'h':
        convert_rgb565_to_png(args)

def delete_temp(args):
    if args.delete_temp == 'true' or args.delete_temp == 'True':
        if os.path.exists("temp"):
            for file in os.scandir("temp"):
                os.remove(file.path)
            print("Removed the PNG files inside the temp folder.")
    else:
        print("Not removed the PNG files inside the temp folder.")

def convert_gif_to_rgb565(args, target_path_list):
    total_image_content = ""
    for target_path in target_path_list:
        name = os.path.basename(args.output_file).rsplit('.', 1)[0]
        png = Image.open(target_path)
        width, height = png.size

        max_line_width = min(width, 1024)
        # print(max_line_width)

        # iterate over the pixels
        image = png.getdata()
        image_content = "{"
        for i, pixel in enumerate(image):
            r = (pixel[0] >> 3) & 0x1F
            g = (pixel[1] >> 2) & 0x3F
            b = (pixel[2] >> 3) & 0x1F
            rgb = r << 11 | g << 5 | b

            if args.swap:
                rgb = ((rgb & 0xFF) << 8) | ((rgb & 0xFF00) >> 8)
            
            image_content += f"0x{rgb:04X}" + (",\n    " if (i % max_line_width == max_line_width-1) else ",")

        if image_content.endswith("\n    "):
            image_content = image_content[:-5]
            
        image_content += "},\n"

        total_image_content += image_content
        
    output_h_content = f"""
// <{width},{height},{len(target_path_list)}>
int gif_frames = {len(target_path_list)};
int gif_width = {width};
int gif_height = {height};
constexpr unsigned short gif_img[][{width*height}] = {{
    {total_image_content}
}};
""".strip() + "\n"

    output_path = os.path.join("header", args.output_file)
    with open(output_path, 'w') as output_file:
        output_file.write(output_h_content)

def resize_img(img_file, resize_value):
    if resize_value == None:
        return img_file
    
    path = os.path.dirname(os.path.abspath(img_file))
    file_name = os.path.basename(img_file)
    img_path = os.path.join(path, file_name)

    # print_image_info("Orignal Image", img_path)
    img = cv2.imread(img_path)

    rs_scale = float(resize_value)
    rs_img = cv2.resize(img, dsize=(0, 0), fx=rs_scale, fy=rs_scale)
    rs_img_path = os.path.join(os.getcwd(), "temp", "resized_" + file_name)
    cv2.imwrite(rs_img_path, rs_img)
                      
    return rs_img_path

def convert_png_to_rgb565(args, target_path):
    name = os.path.basename(args.output_file).rsplit('.', 1)[0]
    png = Image.open(target_path)
    width, height = png.size

    max_line_width = min(width, 64)

    # iterate over the pixels
    image = png.getdata()
    image_content = ""
    for i, pixel in enumerate(image):
        r = (pixel[0] >> 3) & 0x1F
        g = (pixel[1] >> 2) & 0x3F
        b = (pixel[2] >> 3) & 0x1F
        rgb = r << 11 | g << 5 | b

        if args.swap:
            rgb = ((rgb & 0xFF) << 8) | ((rgb & 0xFF00) >> 8)
        
        image_content += f"0x{rgb:04X}" + (",\n    " if (i % max_line_width == max_line_width-1) else ",")

    if image_content.endswith("\n    "):
        image_content = image_content[:-5]

    output_h_content = f"""
// <{width},{height}>
int {name}_width = {width};
int {name}_height = {height};
constexpr unsigned short {name}[{width*height}] = {{
    {image_content}
}};
""".strip() + "\n"

    output_path = os.path.join("header", args.output_file)
    with open(output_path, 'w') as output_file:
        output_file.write(output_h_content)

def convert_rgb565_to_png(args):
    with open(args.input_file, 'r') as input_file:
        tmp = input_file.read()
        icon_size = tmp.split('<')[1].split('>')[0].split(',')
        tmp = tmp.split('{')[1].split('}')[0].split('\n')
        input_content = ""
        for line in tmp:
            input_content += line.split('//')[0].strip()
        input_content = input_content[0:-1].replace(', ', ',').split(',')

        width = int(icon_size[0])
        height = int(icon_size[1])
        png = Image.new('RGB', (width, height))

        for i, word in enumerate(input_content):
            r = (int(word, 16) >> 11) & 0x1F
            g = (int(word, 16) >> 5) & 0x3F
            b = (int(word, 16)) & 0x1F
            png.putpixel((i % width, i // width), (r << 3, g << 2, b << 3))

        output_path = os.path.join("img", args.output_file)
        png.save(output_path)


def convert_gif_to_png(args):
    temp_img_list = []
    input_basename = os.path.basename(args.input_file).rsplit('.', 1)
    if input_basename[1] != 'gif':
        print(f'it is not gif file, {args.input_file}')
        return

    with Image.open(args.input_file) as img:

        print(f'frame count: {img.n_frames}')
        for i in range(img.n_frames):

            img.seek(i)
   
            image = img.convert("RGBA")
            new_data = []

            for item in image.getdata():
                new_data.append(tuple(item[:3]))

            new_img = Image.new("RGB", img.size)
            new_img.putdata(new_data)
            new_img = img.convert("RGBA")

            temp_img_file_name = '{}_{}.png'.format(input_basename[0], i)
            temp_img_path = os.path.join('temp', temp_img_file_name)
            new_img.save(temp_img_path)
            temp_img_list.append(temp_img_path)
    
    return temp_img_list


def print_image_info(name, img_path):
    image = cv2.imread(img_path)

    print(f'============ {name} ============')
    print('Image size : {}'.format(image.shape))
    print('Image dtype : {}'.format(image.dtype))
    print('Image width : {}'.format(image.shape[1]))
    print('Image height : {}'.format(image.shape[0]))
    print('Image total pixels : {}'.format(image.size))
    print('=======================================')

if __name__ == '__main__':
    main()