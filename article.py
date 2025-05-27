# Set up an article class to hold the data from the article
class Article:
    def __init__(self, source):
        self.source = source
        self.header = ''
        self.subheader = ''
        self.author = ''
        self.time = ''
        self.paragraphs = ''
    def __str__(self):
        return f'\n{self.source}\n\n{self.header}\n{self.subheader}\n{self.author}\n{self.time}\n{self.paragraphs}'