import sys
import datetime
from xml.etree import ElementTree

import mediawiki_parser.preprocessor, mediawiki_parser.text
from pijnu.library.node import Nil, Nodes, Node
from mediawiki_parser import wikitextParser
from mw_apostrophes import parse as parse_apostrophes
from mw_constants import html_entities
import py3compat

from bs4 import BeautifulSoup

from clean import WHITELIST_REGEX, COMPRESS_REGEXES

from multiprocessing import Pool, Process, Queue

def toolset():
    tags_stack = []

    style_tags = {'bold': '*', 'bold_close': '*', 'italic': '_', 'italic_close': '_'}

    def render_tag_p(attributes):
        return '\n'

    def render_tag_br(attributes):
        return '\n'

    allowed_tags = {'p': render_tag_p,
                    'br': render_tag_br}

    def content(node):
        return parse_apostrophes('%s' % node.leaf(), style_tags)

    def render_title1(node):
        node.value = ''

    def render_title2(node):
        node.value = ''

    def render_title3(node):
        node.value = ''

    def render_title4(node):
        node.value = ''

    def render_title5(node):
        node.value = ''

    def render_title6(node):
        node.value = ''

    def render_raw_text(node):
        pass

    def render_paragraph(node):
        node.value = '%s\n' % node.leaf()

    def render_wikitext(node):
        pass

    def render_body(node):
        node.value = parse_apostrophes('%s' % node.leaves(), style_tags)

    def render_entity(node):
        value = '%s' % node.leaf()
        if value in html_entities:
            node.value = '%s' % py3compat.unichr(html_entities[value])
        else:
            node.value = '&amp;%s;' % value

    def render_lt(node):
        node.value = '<'

    def render_gt(node):
        node.value = '>'

    def process_attribute(node, allowed_tag):
        assert len(node.value) in [1,2], "Bad AST shape!"
        if len(node.value) == 1:
            attribute_name = node.value[0].value
            return '%s' % attribute_name
        elif len(node.value) == 2:
            attribute_name = node.value[0].value
            attribute_value = node.value[1].value
            return '%s="%s"' % (attribute_name, attribute_value)

    def process_attributes(node, allowed_tag):
        result = ''
        if len(node.value) == 1:
            pass
        elif len(node.value) == 2:
            attributes = node.value[1].value
            for i in range(len(attributes)):
                attribute = process_attribute(attributes[i], allowed_tag)
                if attribute != '':
                    result += ' ' + attribute
        else:
            raise Exception("Bad AST shape!")
        return result

    def render_attribute(node):
        node.value = process_attribute(node, True)

    def render_tag_open(node):
        node.value = ''

    def render_tag_close(node):
        node.value = ''

    def render_tag_autoclose(node):
        node.value = ''

    def render_table(node):
        node.value = ''

    def render_cell_content(node):
        return ''

    def render_table_header_cell(node):
        node.value = ''

    def render_table_normal_cell(node):
        node.value = ''

    def render_table_empty_cell(node):
        node.value = ''

    def render_table_caption(node):
        node.value = ''

    def render_table_line_break(node):
        node.value = '\n'

    def render_preformatted(node):
        node.value = ''

    def render_source(node):
        # Force skip all that
        node.value = ''

    def render_source_open(node):
        node.value = ''

    def render_source_text(node):
        node.value = content(node)

    def render_hr(node):
        node.value = ''

    def render_ul(list, level):
        result = '\n'
        for i in range(len(list)):
            result += content(list[i]) + '\n'
        return result

    def render_ol(list, level):
        result = '\n'
        for i in range(len(list)):
            result += content(list[i]) + '\n'
        return result

    def render_dd(list, level):
        result = '\n'
        for i in range(len(list)):
            result += content(list[i]) + '\n'
        return result

    def render_dt(list, level):
        result = '\n'
        for i in range(len(list)):
            result += content(list[i]) + '\n'
        return result

    def collapse_list(list):
        i = 0
        while i+1 < len(list):
            if list[i].tag == 'bullet_list_leaf' and list[i+1].tag == '@bullet_sub_list@' or \
               list[i].tag == 'number_list_leaf' and list[i+1].tag == '@number_sub_list@' or \
               list[i].tag == 'colon_list_leaf' and list[i+1].tag == '@colon_sub_list@' or \
               list[i].tag == 'semi_colon_list_leaf' and list[i+1].tag == '@semi_colon_sub_list@':
                #list[i].value.append(list[i+1].value[0])
                list.pop(i+1)
            else:
                i += 1
        for i in range(len(list)):
            if isinstance(list[i].value, Nodes):
                collapse_list(list[i].value)

    def select_items(nodes, i, value, level):
        list_tags = ['bullet_list_leaf', 'number_list_leaf', 'colon_list_leaf', 'semi_colon_list_leaf']
        list_tags.remove(value)
        if isinstance(nodes[i].value, Nodes):
            render_lists(nodes[i].value, level + 1)
        items = [nodes[i]]
        while i + 1 < len(nodes) and nodes[i+1].tag not in list_tags:
            if isinstance(nodes[i+1].value, Nodes):
                render_lists(nodes[i+1].value, level + 1)
            items.append(nodes.pop(i+1))
        return items

    def render_lists(list, level):
        i = 0
        while i < len(list):
            if list[i].tag == 'bullet_list_leaf' or list[i].tag == '@bullet_sub_list@':
                list[i].value = render_ul(select_items(list, i, 'bullet_list_leaf', level), level)
            elif list[i].tag == 'number_list_leaf' or list[i].tag == '@number_sub_list@':
                list[i].value = render_ol(select_items(list, i, 'number_list_leaf', level), level)
            elif list[i].tag == 'colon_list_leaf' or list[i].tag == '@colon_sub_list@':
                list[i].value = render_dd(select_items(list, i, 'colon_list_leaf', level), level)
            elif list[i].tag == 'semi_colon_list_leaf' or list[i].tag == '@semi_colon_sub_list@':
                list[i].value = render_dt(select_items(list, i, 'semi_colon_list_leaf', level), level)
            i += 1

    def render_list(node):
        assert isinstance(node.value, Nodes), "Bad AST shape!"
        collapse_list(node.value)
        render_lists(node.value, 1)

    def render_url(node):
        node.value = node.leaf()

    def render_external_link(node):
        if len(node.value) == 1:
            text = node.leaf()
        else:
            text = node.value[1].leaf()

        node.value = text

    def render_interwiki(prefix, page):
        pass

    def render_category(category_name):
        pass

    def render_file(file_name, arguments):
        return ''

    def render_internal_link(node):
        page_name = node.value.pop(0).value
        specified_name = None
        try:
            rest = node.value.pop(0).value[0].value[0]
            if rest.tag == "raw_text":
                specified_name = rest.value
        except:
            pass

        if page_name[0] == ':':
            page_name = page_name[1:]

        if ':' in page_name:
            namespace, page_name = page_name.split(':', 1)
            text = page_name

        if len(node.value) == 0:
            text = page_name
        else:
            text = ''  # Something's wrong

        node.value = specified_name or text

    def render_invalid(node):
        pass

    return locals()


def parse_mediawiki_to_text(text):
    text = text.strip()
    if text.startswith("#REDIRECT"):
        return None

    try:
        preprocessed = mw_preprocessor.parse(element.text)
        text = mw_parser.parse(preprocessed.leaves())
    except:
        return None

    soup = BeautifulSoup(text.value, "html.parser")
    text = ''.join(soup.findAll(text=True))

    text = WHITELIST_REGEX.sub(' ', text)
    for regex, char in COMPRESS_REGEXES:
        text = regex.sub(char, text)

    return text


def parse_mediawiki_tree(input_file, output_file):
    count = 0
    xml_parser = ElementTree.iterparse(input_file)

    mw_preprocessor = mediawiki_parser.preprocessor.make_parser({})
    mw_parser = wikitextParser.make_parser(toolset())

    output = open(output_file, 'w', encoding='utf-8')

    for event in xml_parser:
        element = event[1]
        if element.tag != "{http://www.mediawiki.org/xml/export-0.10/}text":
            continue

        text = element.text
        input_size = len(text)

        text = parse_mediawiki_to_text(text)
        if text is None:
            continue

        output.write(text)
        count += 1

        output_size = len(text)
        factor = (output_size / input_size) * 100

        timestamp = datetime.datetime.now().time().strftime("%H:%m:%S")
        print(f"[{timestamp}] Parsed {count} articles, minified to {factor:.01f}% ({input_size} -> {output_size} bytes)")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("./wikiscraper.py INPUT OUTPUT")
        print("OUTPUT will be overwritten.")
        exit()

    parse_mediawiki_tree(sys.argv[1], sys.argv[2])
