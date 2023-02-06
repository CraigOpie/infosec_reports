import textwrap


class TextBox:
    def __init__(self, text, width):
        self.text = text
        self.width = width
        self.string_list = self._generate_list()

    def __getitem__(self, item):
        return self.string_list[item]

    def _generate_list(self):
        # Split the input text into separate paragraphs before formatting the
        # length.
        paragraph_list = self.text.split("\n")
        text_list = []
        for paragraph in paragraph_list:
            text_list += textwrap.fill(paragraph, self.width, replace_whitespace=False).split("\n")
        text_list = [line.ljust(self.width) for line in text_list]
        return text_list

    def update_width(self, width):
        self.width = width
        self.string_list = self._generate_list()
