#!/usr/bin/env python
import sys
import re


class ConvertTextToHtml():
    def __init__(self):
        self.output_file = file(sys.argv[2], 'w')
        self.input_file = file(sys.argv[1], 'r+')
        self.output_file = file(sys.argv[2], 'a')
        self.lang_flag = sys.argv[3]
        self.list_num_regex = re.compile(r"(\d+)\s.*")

    def write_to_file(self, line):
        if not self.output_file.closed:
            self.output_file.write(line)
        else:
            print "problem in opening file"

    def make_h2_header(self, line):
        line = "<h2>" + line + "</h2>"
        self.write_to_file(line)
        self.write_to_file("\n")

    def make_h3_header(self, line):
        line = "<h3>" + line + "</h3>"
        self.write_to_file(line)
        self.write_to_file("\n")

    def make_start_code_block(self, line):
        line = "<pre><code>" + "\n" + line
        self.write_to_file(line)
        self.write_to_file("\n")

    def make_end_code_block(self, line):
        line = line + "\n" + "</code></pre>"
        self.write_to_file(line)
        self.write_to_file("\n")

    def make_code_block(self, line):
        self.open_code_block_encountered = not self.open_code_block_encountered

        if self.open_code_block_encountered:
            self.code_block = True
            if self.lang_flag in line:
                self.make_start_code_block(line)
        else:
            self.code_block = False
            if self.lang_flag in line:
                self.make_end_code_block(line)

    def make_code_snippet(self, line):
        self.write_to_file(line.rstrip())
        self.write_to_file("\n")

    def make_quote_word(self, word):
        result = "<span class='quoted'>" + word + "</span>"
        self.write_to_file(result)
        self.write_to_file(" ")

    def make_end_quote(self, word):
        self.quote_open = False
        self.quoted_line = self.quoted_line + " " + word + "</span>" + " "
        self.write_to_file(self.quoted_line)
        self.quoted_line = ""

    def is_a_quoted_word(self, word):
        if ((word.startswith("\"") or word.startswith("'")) and
                (word.endswith("\"") or word.endswith("'") or word.endswith(".") or word.endswith(","))):
            return True
        return False

    def make_quoted_string(self, line):
        self.quote_open = False
        self.quoted_line = ""
        for word in line.split():
            if self.is_a_quoted_word(word):
                self.make_quote_word(word)
            elif word.startswith("\"") or word.startswith("'"):
                self.quote_open = True
                self.quoted_line = self.quoted_line + " " + "<span class='quoted'>" + word
            elif word.endswith("\"") or word.endswith("'"):
                self.make_end_quote(word)
            elif (word.endswith(".") or word.endswith(",")) and ("\"" or "'") in word:
                self.make_end_quote(word)
            else:
                if self.quote_open:
                    self.quoted_line += " " + word
                else:
                    self.write_to_file(word)
                    self.write_to_file(" ")

        self.write_to_file("\n")

    def complete_list(self, line):
        if self.list_string != "":
            line = "<li>" + line + "</li>"
            self.write_to_file(line)
            self.write_to_file("\n")
            self.list_start = False
            self.list_string = ""

    def open_unordered_list(self):
        self.is_unordered_list_open = True
        self.write_to_file("<ul>")
        self.write_to_file("\n")

    def close_unordered_list(self):
        if self.is_unordered_list_open:
            self.write_to_file("</ul>")
            self.write_to_file("\n")
            self.is_unordered_list_open = False

    def get_list_number(self, line):
        match_obj = self.list_num_regex.match(line)
        if match_obj:
            return match_obj.group(1)

    def process_file(self):
        line_count = int(self.input_file.readline())
        self.file_line_count = line_count
        raw_line = self.input_file.readline()
        line = raw_line.strip()
        count = 0
        self.is_unordered_list_open = False
        self.list_start = False
        self.list_string = ""
        self.pre_tag_start = False
        self.open_code_block_encountered = False
        self.code_block = False
        while line or count < self.file_line_count:
            if line:
                if "<pre>" in line:
                    self.pre_tag_start = True
                    self.write_to_file(raw_line.rstrip())
                    self.write_to_file("\n")
                elif "</pre>" in line:
                    self.pre_tag_start = False
                    self.write_to_file(raw_line.rstrip())
                    self.write_to_file("\n")

                elif self.pre_tag_start:
                    self.write_to_file(raw_line.rstrip())
                    self.write_to_file("\n")

                elif line[0].isdigit():
                    list_number = self.get_list_number(line)
                    if list_number == 1:
                        self.open_unordered_list()
                    self.complete_list(self.list_string)
                    self.list_start = not self.list_start
                    if self.list_start:
                        self.list_string += " " + line

                elif line[-1] == ':' and ("**" not in line):
                    self.complete_list(self.list_string)
                    self.close_unordered_list()
                    line = line[:-1]
                    self.make_h2_header(line)

                elif "**" in line:
                    self.complete_list(self.list_string)
                    self.close_unordered_list()
                    line = line.replace("**", "")
                    self.make_h3_header(line)

                else:
                    if line.startswith("========"):
                        self.complete_list(self.list_string)
                        self.close_unordered_list()
                        pass
                    elif line.startswith("["):
                        self.complete_list(self.list_string)
                        self.close_unordered_list()
                        self.make_code_block(line)

                    elif self.code_block and self.open_code_block_encountered:
                        self.complete_list(self.list_string)
                        self.close_unordered_list()
                        self.make_code_snippet(raw_line.rstrip())

                    else:
                        if self.list_start:
                            self.list_string += " " + line
                        elif '"' in line or "'" in line:
                            self.make_quoted_string(line)
                        else:
                            self.write_to_file(line)
            elif line == '':
                self.complete_list(self.list_string)
                self.close_unordered_list()
                self.write_to_file("\n")

            raw_line = self.input_file.readline()
            line = raw_line.strip()
            count += 1
            # print 'line is: ', line


if __name__ == "__main__":
    if len(sys.argv) >= 4:

        text_to_html = ConvertTextToHtml()
        text_to_html.process_file()
    else:
        print "Please provide 3 arguments"