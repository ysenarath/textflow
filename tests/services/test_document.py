""" Test Model - Document """
import html

from textflow.model import Document


def test_document_insert():
    text = 'This is a sample document.'
    doc = Document(id=0, text=text)
    assert doc.text == text


def test_document_insert_html():
    text = 'This is a sample <span>document</span>.'
    doc = Document(id=0, text=text)
    assert doc.text == html.escape(text)
