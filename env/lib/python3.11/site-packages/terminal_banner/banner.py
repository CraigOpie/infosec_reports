import subprocess
import terminal_banner as tb


class Banner:
    kw_defaults = {
        'border_char': '*',
        'max_width': None,
        'min_width': None
    }

    def __init__(self, text, **kwargs):
        for key in Banner.kw_defaults:
            setattr(self, key, kwargs[key] if key in kwargs else self.kw_defaults[key])
        self.text = text
        self.width = None
        self.text_box = None

    def __str__(self):
        self._reset()
        return self._banner_string()

    def _banner_string(self):
        output_string = self.border_char * self.width + "\n"
        for text_line in self.text_box:
            output_string += self.border_char + " " + text_line + " " + self.border_char + "\n"
        output_string += self.border_char * self.width
        return output_string

    def _reset(self):
        self.width = self._calculate_width()
        self.text_box = tb.TextBox(self.text, self.width - 4)

    def _calculate_width(self):
        width = get_terminal_width()

        if self.max_width:
            width = min(width, self.max_width)

        if self.min_width:
            width = max(width, self.min_width)

        return width


def get_terminal_width():
    return int(subprocess.check_output(['stty', 'size']).split()[1])
