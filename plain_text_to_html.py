#!/usr/bin/env python
import sys


class ConvertTextToHtml():
    def __init__(self):
        self.output_file = file(sys.argv[2], 'w')
        self.input_file = file(sys.argv[1], 'r+')
        self.output_file = file(sys.argv[2], 'a')
        self.lang_flag = sys.argv[3]
        self.file_line_count = 1865

    def write_to_file(self, line):
        if not self.output_file.closed:
            self.output_file.write(line)
        else:
            print "problem in opening file"

    def make_header(self, line):
        line = "<h2>" + line + "</h2>"
        return line

    def make_list(self, line):
        line = "<li>" + line + "</li>"
        return line

    def process_file(self):
        raw_line = self.input_file.readline()
        line = raw_line.strip()
        count = 0
        open_code_block_encountered = False
        code_block = False
        while line or count < self.file_line_count:
            if line:
                if line[-1] == ':':
                    line = line[:-1]
                    line = self.make_header(line)
                    self.write_to_file(line)
                    self.write_to_file("\n")
                elif line[0].isdigit():
                    line = self.make_list(line)
                    self.write_to_file(line)
                    self.write_to_file("\n")
                else:
                    if line.startswith("========"):
                        pass
                    elif line.startswith("["):
                        open_code_block_encountered = not open_code_block_encountered

                        if open_code_block_encountered:
                            code_block = True
                            if self.lang_flag in line:
                                line = "<pre><code>" + "\n" + line
                                self.write_to_file(line)
                                self.write_to_file("\n")
                        else:
                            code_block = False
                            if self.lang_flag in line:
                                line = line + "\n" + "</code></pre>"
                                self.write_to_file(line)
                                self.write_to_file("\n")
                    elif code_block and open_code_block_encountered:
                        print 'this line is coming here', raw_line.rstrip()
                        self.write_to_file(raw_line.rstrip())
                        self.write_to_file("\n")

                    else:
                        quote_open = False
                        quoted_line = ""
                        for word in line.split():
                            if word.startswith("\"") and (word.endswith("\"") or word.endswith(".") or word.endswith(",")):
                                result = "<span class='quoted'>" + word  + "</span>"
                                self.write_to_file(result)
                                self.write_to_file(" ")
                            elif word.startswith("\""):
                                quote_open = True
                                quoted_line = quoted_line + " " + "<span class='quoted'>" + word
                            elif word.endswith("\""):
                                quote_open = False
                                quoted_line = quoted_line + " " + word + "</span>" + " "
                                self.write_to_file(quoted_line)
                                quoted_line = ""
                            elif (word.endswith(".") or word.endswith(",")) and "\"" in word:
                                quote_open = False
                                quoted_line = quoted_line + " " + word + "</span>" + " "
                                self.write_to_file(quoted_line)
                                quoted_line = ""
                            else:
                                if quote_open:
                                    quoted_line += " " +word
                                else:
                                    self.write_to_file(word)
                                    self.write_to_file(" ")
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