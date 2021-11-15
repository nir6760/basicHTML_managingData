import os
import hw1_utils
from pdfminer import high_level
import pathlib
from urllib.parse import unquote


# get all pdf files recursively
def get_all_pdf_files():
    all_files = []
    for dirpath, dirnames, filenames in os.walk("pdfs"):
        for filename in [f for f in filenames if f.endswith(".pdf")]:
            all_files.append(os.path.join(dirpath, filename))
    return all_files


# find file path by name
def find_file_path_by_name(file_name_in):
    for dirpath, dirnames, filenames in os.walk("pdfs"):
        for filename in [f for f in filenames if f.endswith(".pdf")]:
            if file_name_in == filename:
                return os.path.join(dirpath, filename)
    return None


# create png html file as string
def create_wordcloud_page(title, png_path):
    content = "<html>\n\
            <head>\n\
                <title>png_page</title>\n\
            </head>\n\
            <body>\n\
            <h1>" + title + " </h1>\n\
            <img src=\"/" + png_path + "\">\n\
            </br></br>\n\
            <button onclick=\"home_red()\">Go back</button>\n\
    <script>\n\
    function home_red() {\n\
        window.location.assign(\"http://localhost:8888\")\n\
    }\n\
    </script >\n\
            </body>\n\
            </html>"
    return content


# create png html file as string
def create_home_page(all_pdf_files):
    content = "<html>\n\
                <head>\n\
                <style>\n\
                li:not(:last-child) {\n\
                    margin-bottom: 20px;\n\
                }\n\
                </style>\n\
                <title>Home Page</title>\n\
            </head>\n\
            <body>\n\
                <h1>Landing Page</h1>\n\
                <p>Welcome to the landing page!</p>\n\
                <p>choose a .pdf file to generate a wordcloud from:</p>\n\
                <ul style=\"list-style-type:disc\">\n"
    for pdf_file_path in all_pdf_files:
        url = unquote(pdf_file_path)
        # pdf_name = os.path.basename(pdf_file_path)
        pdf_name = pathlib.Path(pdf_file_path)
        pdf_name = pathlib.Path(*pdf_name.parts[1:])  # remove pdfs// from path
        pdf_name = str(pdf_name)
        # pdf_name = pdf_file_path[5:]
        pdf_name_without_ext = os.path.splitext(pdf_name)[0]
        pdf_name_without_ext = '\'' + pdf_name_without_ext + '\''
        if os.sep == '\\':  # windows
            pdf_name_without_ext = pdf_name_without_ext.replace('\\', '/')
        content_li = "<li><button onclick=\"myFunction(" + pdf_name_without_ext + ")\">" + pdf_name + "</button></li>\n"
        content += content_li
    content += "</ul>\n\
                <script>\n\
                function myFunction(file_name){\n\
                    location.replace(\"http://localhost:8888/\" + file_name);\n\
                }\n\
                </script>\n\
            </body>\n\
            </html>"
    return content


# read pdf file from pdf path and create wordcloud png
def pdf_to_wordcloud(pdf_path, stop_words_list):
    pdf_name = os.path.split(pdf_path)[1]
    pdf_string = high_level.extract_text(pdf_path)
    pdf_string = pdf_string.lower()  # all lower case, wordcloud will be lower case
    pdf_string_filtered = [word for word in pdf_string.split() if not word in stop_words_list]
    pdf_string_filtered = " ".join(pdf_string_filtered)
    saving_folder_png = os.path.join('html_pages', 'png_images')
    os.makedirs(saving_folder_png, exist_ok=True)
    png_path = os.path.join(saving_folder_png, os.path.splitext(pdf_name)[0] + '.png')
    hw1_utils.generate_wordcloud_to_file(pdf_string_filtered, png_path)
    return png_path


class HTTPHandler:
    def get(self, filename, file_type):

        with open('stopwords.txt') as text_file:
            stop_words_list = text_file.read().split()
        if not os.path.isdir('pdfs'): # pdfs folder doesnt exist
           print('pdfs folder dosn\'t exist')
           raise FileNotFoundError
        all_pdf_files = get_all_pdf_files()
        if file_type.find("image") == -1:
            if filename == '/':
                content = create_home_page(all_pdf_files)
            else:
                filename += ".pdf"
                components = filename[1:].split('/')
                file_path_rel_pdfs = os.path.join(*components)
                file_path = os.path.join('pdfs', *components)
                # file_path = find_file_path_by_name(file_path)
                if file_path not in all_pdf_files:
                    raise FileNotFoundError
                png_path = pdf_to_wordcloud(file_path, stop_words_list)  # creates the png
                content = create_wordcloud_page(file_path_rel_pdfs, png_path)

        else:  # this is image
            image_data = open(filename[1:], 'rb')  # file name is png path
            bytes = image_data.read()
            # Content-Type: image/jpeg, image/png \n\n
            content = bytes
            image_data.close()
            return content

        # Read file contents
        return content
