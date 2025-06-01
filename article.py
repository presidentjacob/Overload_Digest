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
    
    def set_header(self, header):
        self.header = header

    def set_subheader(self, subheader):
        self.subheader = subheader

    def set_author(self, author):
        self.author = author

    def set_time(self, time):
        self.time = time

    def set_paragraphs(self, paragraphs):
        if self.paragraphs:
            self.paragraphs += '\n\n' + paragraphs
        else:
            self.paragraphs = paragraphs

    def logging_info(self):
        return f'Article {self.header} scraped.'

# CNN Article, NPR Article, FOX NEWS Article, TechCrunch Article, Wired Article, Four Zero Four Media Article, BBC Article, CBS Article, and ABC Article classes 
# inherit from the base Article class.
class CNNArticle(Article):
    def __init__(self):
        super().__init__('CNN')

    def __str__(self):
        return f'\n{self.source}\n\n{self.header}\n{self.author}\n{self.time}\n{self.paragraphs}'

    def set_header(self, header):
        super().set_header(header)
    
    def set_author(self, author):
        super().set_author(author)
    
    def set_time(self, time):
        super().set_time(time)
    
    def set_paragraphs(self, paragraphs):
        super().set_paragraphs(paragraphs)

    def logging_info(self):
        return f'CNN Article {self.header} scraped.'

class NPRArticle(Article):
    def __init__(self):
        super().__init__('NPR')

    def __str__(self):
        return f'\n{self.source}\n\n{self.header}\n{self.author}\n{self.time}\n{self.paragraphs}'

    def set_header(self, header):
        super().set_header(header)
    
    def set_author(self, author):
        super().set_author(author)
    
    def set_time(self, time):
        super().set_time(time)
    
    def set_paragraphs(self, paragraphs):
        super().set_paragraphs(paragraphs)

    def logging_info(self):
        return f'NPR Article {self.header} scraped.'

class FoxArticle(Article):
    def __init__(self):
        super().__init__('FOX NEWS')

    def __str__(self):
        return f'\n{self.source}\n\n{self.header}\n{self.subheader}\n{self.author}\n{self.time}\n{self.paragraphs}'
    
    def set_header(self, header):
        super().set_header(header)

    def set_subheader(self, subheader):
        super().set_subheader(subheader)

    def set_author(self, author):
        super().set_author(author)

    def set_time(self, time):
        super().set_time(time)

    def set_paragraphs(self, paragraphs):
        super().set_paragraphs(paragraphs)

    def logging_info(self):
        return f'FOX NEWS Article {self.header} scraped.'

class TechCrunchArticle(Article):
    def __init__(self):
        super().__init__('TECHCRUNCH')

    def __str__(self):
        return f'\n{self.source}\n\n{self.header}\n{self.author}\n{self.time}\n{self.paragraphs}'

    def set_header(self, header):
        super().set_header(header)
    
    def set_author(self, author):
        super().set_author(author)
    
    def set_time(self, time):
        super().set_time(time)
    
    def set_paragraphs(self, paragraphs):
        super().set_paragraphs(paragraphs)

    def logging_info(self):
        return f'TechCrunch Article {self.header} scraped.'

class WiredArticle(Article):
    def __init__(self):
        super().__init__('WIRED')

    def __str__(self):
        return f'\n{self.source}\n\n{self.header}\n{self.author}\n{self.time}\n{self.paragraphs}'

    def set_header(self, header):
        super().set_header(header)
    
    def set_author(self, author):
        super().set_author(author)
    
    def set_time(self, time):
        super().set_time(time)
    
    def set_paragraphs(self, paragraphs):
        super().set_paragraphs(paragraphs)

    def logging_info(self):
        return f'Wired Article {self.header} scraped.'
    
class FourZeroFourMediaArticle(Article):
    def __init__(self):
        super().__init__('404 MEDIA')

    def __str__(self):
        return f'\n{self.source}\n\n{self.header}\n{self.author}\n{self.time}\n{self.paragraphs}'

    def set_header(self, header):
        super().set_header(header)

    def set_subheader(self, subheader):
        super().set_subheader(subheader)
    
    def set_author(self, author):
        super().set_author(author)
    
    def set_time(self, time):
        super().set_time(time)
    
    def set_paragraphs(self, paragraphs):
        super().set_paragraphs(paragraphs)

    def logging_info(self):
        return f'Four Zero Four Media Article {self.header} scraped.'
    
class BBCArticle(Article):
    def __init__(self):
        super().__init__('BBC NEWS')

    def __str__(self):
        return f'\n{self.source}\n\n{self.header}\n{self.author}\n{self.time}\n{self.paragraphs}'

    def set_header(self, header):
        super().set_header(header)
    
    def set_author(self, author):
        super().set_author(author)
    
    def set_time(self, time):
        super().set_time(time)
    
    def set_paragraphs(self, paragraphs):
        super().set_paragraphs(paragraphs)

    def logging_info(self):
        return f'BBC Article {self.header} scraped.'
    
class CBSArticle(Article):
    def __init__(self):
        super().__init__('CBS NEWS')

    def __str__(self):
        return f'\n{self.source}\n\n{self.header}\n{self.author}\n{self.time}\n{self.paragraphs}'

    def set_header(self, header):
        super().set_header(header)
    
    def set_author(self, author):
        super().set_author(author)
    
    def set_time(self, time):
        super().set_time(time)
    
    def set_paragraphs(self, paragraphs):
        super().set_paragraphs(paragraphs)

    def logging_info(self):
        return f'CBS Article {self.header} scraped.'
    
class ABCArticle(Article):
    def __init__(self):
        super().__init__('ABC NEWS')

    def __str__(self):
        return f'\n{self.source}\n\n{self.header}\n\n{self.author}\n\n{self.time}\n\n{self.paragraphs}'

    def set_header(self, header):
        super().set_header(header)

    def set_author(self, author):
        super().set_author(author)
    
    def set_time(self, time):
        super().set_time(time)
    
    def set_paragraphs(self, paragraphs):
        super().set_paragraphs(paragraphs)

    def logging_info(self):
        return f'ABC Article {self.header} scraped.'