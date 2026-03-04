from pathlib import Path
import ebooklib
from ebooklib import epub
# from wtpsplit import SaT
from lxml import etree

def read_book(book_path: Path) -> epub.EpubBook:
    return epub.read_epub(book_path)

def get_document(book: epub.EpubBook) -> list[epub.EpubHtml]:
    return [item for item in book.get_items() if item.get_type() == ebooklib.ITEM_DOCUMENT]



if __name__ == "__main__":
    book_path = Path("../books/金閣寺 (三島由紀夫) (Z-Library).epub")
    book = read_book(book_path)
    documents = get_document(book)
    test_xpath = "//p/text()"
    # print(documents[7].content.decode("utf-8"))
    tree = etree.HTML(documents[7].content)
    result = tree.xpath(test_xpath)
    whole_text = "".join(result)
    print(sat.split(whole_text))
    # print(whole_text)
    # print(result)
    # print(documents[7].content.decode("utf-8"))