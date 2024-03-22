import re

path = '.'
inputfilename = 'vstup-emco-sk-cp1250.tsv'
outputfilename = 'vystup-emco-sk.csv'
failedlinefilename = 'nepodarene-emco-sk.csv'
inputencoding = 'cp1250'
NEWLINE = '\n'
ITEM_DELIMITER = '\t'

path += '/'

print('Zpracování souboru: ', path+inputfilename)
print('Vstupní kódování: ', inputencoding, ' oddělovač záznamů: tabulátor')

def reset_invalidlinesfile():
    with open(path+failedlinefilename, 'w') as file:
        file.write('')

def append_text_to_failedlines_file(text):
    with open(path+failedlinefilename, 'a') as file:
        file.write(text+NEWLINE)

def parse_inner_text(inner_text, output_row, field_names, id):
    #output_row['ID'] = id
    if 'Data' not in field_names:
        field_names.append('Data')
    inner_text = inner_text.replace('<br>', '')
    inner_text = re.sub(r'([0-9],?[0-9]*) ?(g|kcal|ml),?:?;?\.? *', r'\1 \2\t', inner_text)
    inner_text = re.sub(r' */ *', '/', inner_text)
    inner_text = re.sub(r':? ([0-9]|&lt;[0-9])', r':;\1', inner_text)

    inner_text = make_first_letter_of_each_nutriitem_capital(inner_text)

    output_row['Data'] = id+ITEM_DELIMITER+inner_text.strip(' \t') 

def make_first_letter_of_each_nutriitem_capital(text):
    blocks = text.split(ITEM_DELIMITER)
    blocks_strip = [item.strip() for item in blocks]
    blocks_first_capital = []
    for item in blocks_strip:
        if item.startswith('z toho'):
            blocks_first_capital.append(item)
        elif len(item) != 0:
            chars = list(item)
            chars[0] = chars[0].capitalize()
            blocks_first_capital.append(''.join(chars))

    text = ITEM_DELIMITER.join(blocks_first_capital)
    return text              

# Heading formats:
#format_full_html = re.compile(r'<strong> *Výživové údaje na 100 g:</strong><br>Energetická hodnota 1860 kJ/444 kcal, <br>Tuky 13 g, <br>z toho nasycené mastné kyseliny 1,4 g, <br>Sacharidy 69 g, <br>z toho cukry 16 g, <br>Vláknina 5,0 g, <br>Bílkoviny 9,8 g, <br>Sůl 0,07 g, <br>Betaglukany 2,5g  <strong>Výživové údaje na jednu porci 45g:</strong><br>Energetická hodnota 837 kJ/200 kcal, <br>Tuky 5,9 g, <br>z toho nasycené mastné kyseliny 0,6 g, <br>Sacharidy 31 g, <br>z toho cukry 7,2 g, <br>Vláknina 2,3 g, <br>Bílkoviny 4,4 g,<br> Sůl 0,03 g <br> Betaglukany 1,1 g <br>*Příznivého účinku se v rámci zdravého životního stylu a různorodého jídelníčku dosáhne konzumací 3 g betaglukanů z ovsa, ovesných otrub, ječmene a ječných otrub za den.  <strong>Návod k přípravě:</strong>  1. Mysli nasypte do misky. 2. Zalijte mlékem nebo jogurtem. 3. Mysli můžete konzumovat i bez úpravy v suchém stavu. 
#[^>]+>')
heading_format_full_html = re.compile(r'^<strong>.*100 ?(g|ml)( ?sm..si ?)?:? ?</strong> *(<br> *)?(.*)(<strong>.*?)??\.?$')    # use 4th group
heading_format_no_html = re.compile(r'^.* na 100 ?(g|ml)( ?v.robku priemerne obsahuje)?:?(.*)(V..ivov. .daje.*)?\.?$')          # use 3rd group
heading_format_plain = re.compile(r'^(Energ.*)\.$')                                                                        # use 1st group
#regex_trailing_vyzivove_hodnoty = re.compile(r'<strong> *Výživové údaje na 100 g:</strong><br>')

def trim_heading_and_parse_content(nutridescription, output_row, fieldnames, id):
    # remove redundant spaces
    text_compacted = re.sub(' {2,}', ' ', nutridescription).strip()
    #text_compacted = re.sub('0 ?g sm..si:', '0 g:', text_compacted)
    if heading_format_full_html.fullmatch(text_compacted):
        inner_text = heading_format_full_html.fullmatch(text_compacted).group(4)
        inner_text = inner_text.split('<strong>')[0]
    elif heading_format_no_html.fullmatch(text_compacted):
        inner_text = heading_format_no_html.fullmatch(text_compacted).group(2)
    elif heading_format_plain.fullmatch(text_compacted):
        inner_text = heading_format_plain.fullmatch(text_compacted).group(1)
    else:
        invalidline = id + ': ' + nutridescription
        #print(invalidline)
        append_text_to_failedlines_file(invalidline)
        return
    parse_inner_text(inner_text.strip(), output_row, fieldnames, id)
    #text_compacted = text_compacted.lstrip(regex_starting_vyzivove_hodnoty).rstrip(regex_trailing_vyzivove_hodnoty)
    #parts = text_with_spaces_compacted.split('</strong>')
    #if format_full_html.match(text_compacted):
    #    nutridescription = parts[1]
    
def load_CSV_with_columns_ID_nutri_line_by_lineCSV(path):
    import csv

    try:
        with open(path+inputfilename, newline=NEWLINE) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=ITEM_DELIMITER)
            output = []

            fieldnames = []
            for row in reader:
                id = row['id']
                nutridescription = row['Nutri']
                #print(id, row['Nutri'])
                newoutputrow = {}
                trim_heading_and_parse_content(nutridescription, newoutputrow, fieldnames, id)
                output.append(newoutputrow)
                #print(newoutputrow)
                #break

    except FileNotFoundError:
        print('Soubor ', path, inputfilename, ' nenalezen!')
        exit(1)
    except KeyError:
        print('Neplatný formát souboru: ', path, inputfilename, ' - chybí sloupec "ID" nebo "Nutri"')
        exit(2)
    with open(path+outputfilename, 'w', newline=NEWLINE, encoding=inputencoding) as outputfile:
        #outputfile = open(path+outputfilename, 'w', newline=newlinedelimiter, encoding=inputencoding)
        #writer = csv.DictWriter(outputfile, fieldnames, delimiter=itemdelimiter, quotechar='"', quoting=csv.QUOTE_MINIMAL)
        #writer.writerows(output)
        for row in output:
            if 'Data' not in row:
                continue
            line = row['Data']
            outputfile.write(line+NEWLINE)
            #print(row['Data'])



def main():
    reset_invalidlinesfile()
    load_CSV_with_columns_ID_nutri_line_by_lineCSV(path)

main()