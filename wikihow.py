import wikihowunofficialapi as wha
import unicodedata

step_list = []
wiki_list = []


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def count_word(sentences):
    words = sentences.split()
    word_count = len(words)
    return word_count


def create_dataset(rows: int) -> dict:
    """
    :param rows:
    :return: dictionary
    """

    for _ in range(0, rows):

        try:
            ra = wha.random_article(lang='es')
            tittle = ra.title
            intro = ra.intro
            methods = ra.methods
            url = 'http://es.wikihow.com/' + remove_accents(tittle).replace(' ', '-').lower()
            intro_len = count_word(intro)

            step_text = ''

            result_dict = {}

            for method in methods:
                step_text += method.title + ': '
                for step in method.steps:
                    step_text += f"{step.number}- {step.title} {step.description} "
            result_dict['steps'] = step_text

            data_row = {
                'title': tittle,
                'url': url,
                'intro': intro,
                'len': intro_len,
                'methods': step_text,
                'len_methods': count_word(step_text)

            }
            wiki_list.append(data_row)

            print(f'Row: {_ + 1} of {rows} was added!')

        except wha.exceptions.ParseError:
            # Handle the ParseError exception here
            print(f"Error parsing article of row {_ + 1}. Skipping to the next one.")
            continue

    if len(wiki_list)==0:
        create_dataset(rows=1)

    print("Spanish dataset has been created!")

    return wiki_list


