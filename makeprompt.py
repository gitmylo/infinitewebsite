import json


def parse_template_field(template_field):
    if isinstance(template_field, str):
        return template_field
    if 'file' in template_field:
        return open(template_field['file'], 'r', encoding='utf8').read()
    if 'raw' in template_field:
        return template_field['raw']
    return ''


def make_prompt_message(url, start):
    return f'''This is a webpage on the "Infinite pages" website.
The "Infinite pages" website contain unlimited pages. As every URL is valid.
The url is: "{url}", write the webpage for "{url}" on a website. The content of the webpage must be relevant to the title.
There are no images on this website, it's all standard markdown, with links.
All pages are AI generated, and not human-made.
All pages must contain at least one link to another page.
Only relative links are allowed. (Example: [page](path/to/page.html))
[Important: Please use a lot of markdown in your response, and include lots of links to other pages.]
{start}'''


def make_prompt(targeturl):
    template = json.load(open('template.json', 'r', encoding='utf8'))
    start = parse_template_field(template['start']).replace('{{pageurl}}', targeturl)
    end = parse_template_field(template['end']).replace('{{pageurl}}', targeturl)
    stop = parse_template_field(template['stoptoken']).replace('{{pageurl}}', targeturl)

    prompt = make_prompt_message(targeturl, start).replace('{{pageurl}}', targeturl)

    return prompt, start, end, stop
