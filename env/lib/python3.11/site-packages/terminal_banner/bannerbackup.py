import subprocess


class BannerBackup:
    def __init__(self, text, max_width=None, align='left', buf_height=None, buf_width=1,
                 border_char='*', border_horizontal_thickness=1, border_vertical_thickness=1,
                 color=None, border_color=None, text_color=None, bg_color=None):
        self.text = text
        self.max_width = max_width
        self.buf_height = buf_height
        self.buf_width = buf_width
        self.border_char = border_char
        self.border_horizontal_thickness = border_horizontal_thickness
        self.border_vertical_thickness = border_vertical_thickness
        self.width = None

    def reset_width(self):
        self.width = self.calc_width()

    def calc_width(self):
        if self.max_width:
            return min(get_terminal_width(), self.max_width)
        else:
            return get_terminal_width()

    def banner_string(self):
        string_builder = ""
        for _ in range(self.border_horizontal_thickness):
            string_builder += self.border_char * self.width + "\n"
        for _ in range(self.buf_height):
            string_builder += self.buffer_line() + "\n"
        string_builder += self.text_lines(self.text) + "\n"
        for _ in range(self.buf_height):
            string_builder += self.buffer_line() + "\n"
        for _ in range(self.border_horizontal_thickness):
            string_builder += self.border_char * self.width + "\n"
        return string_builder.rstrip("\n")

    def border_line(self):
        return self.border_char * self.width

    def buffer_line(self):
        return self.text_lines()

    def text_lines(self, text=""):
        text_string = ""
        text_string += self.border_vertical_thickness * self.border_char
        text_string += " " * self.buf_width
        text_string += text
        text_string += " " * (self.width - len(text_string) - self.border_vertical_thickness)
        text_string += self.border_vertical_thickness * self.border_char
        return text_string

    def __str__(self):
        self.reset_width()
        return self.banner_string()


def get_terminal_width():
    return int(subprocess.check_output(['stty', 'size']).split()[1])
