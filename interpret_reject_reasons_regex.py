#!/usr/bin/env python3
""" This script reads and interprets the rejected reasons file """

import argparse
import re
import json

# CLI Args
parser = argparse.ArgumentParser(description='Reads the Rejected reasons file')
parser.add_argument(
        'file',
        metavar='f',
        type=str,
        help='file to read')

parser.add_argument(
        'ofile',
        metavar='of',
        type=str,
        help='output file')

# RegEx!!
r_fields = re.compile(r'(Seg\w*)\|([^|]*)\|')
r_rejects = re.compile(
    r' \d+\|\|\w+\|\|\d+ ((?! \d+\|\|\w+\|\|\d+ |\| WARNING REASONS).)+'
)
r_warnings = re.compile(r' \d+\|\|\w+ ((?!( \d+\|\|)|(\|  \|)).)+')


# Why python? why?!
def force_extract_re(source: str, regex: re.Pattern):
    """ Extract regex matches """
    return list(map(
        lambda r: r.group(),
        regex.finditer(source)))


def interpret_row(row: str):
    """ Returns the data of single record """
    fields = r_fields.findall(row)
    reject_reasons = force_extract_re(row, r_rejects)
    warnings = force_extract_re(row, r_warnings)
    return fields, reject_reasons, warnings


def load(path: str, columns: list = None):
    """ Loads the data """
    content = None
    with open(path, 'rt', encoding='latin-1') as file_stram:
        content = file_stram.readlines()

    content = filter(
            lambda l: l,
            map(lambda l: l.replace('\n', ''), content))

    # Save metadata
    metadata = next(content)
    iterator = 0
    metadata_text = ''
    metadata = metadata.split('|')

    for val in metadata:
        val = val.strip()
        if val:
            if iterator % 2 == 0:
                metadata_text += val + ':\n' + ' ' * 4
            else:
                metadata_text += val + '\n'
        iterator += 1

    with open('rejectReasons_metadata.txt', 'wt', encoding='latin-1') as mfile:
        mfile.write(metadata_text)

    # Construct file content
    content = map(interpret_row, content)
    if not columns:
        first_row = next(content)
        data = {t[0]: [t[1]] for t in first_row[0]}
        data['REJECT REASONS'] = [json.dumps(first_row[1])]
        data['WARNING REASONS'] = [json.dumps(first_row[2])]
    else:
        data = {c: [] for c in columns}

    print('Construyendo dataset.')
    n_keys = len(data.keys())
    for fields, rejects, warnings in content:
        cols = set(['REJECT REASONS', 'WARNING REASONS'])

        for col, val in fields:
            if col not in data:
                data[col] = []
            data[col] += [val if val else '']
            cols.add(col)

        data['REJECT REASONS'] += [json.dumps(rejects) if rejects else '']
        data['WARNING REASONS'] += [json.dumps(warnings) if warnings else '']

        for mcl in set(data.keys()).difference(cols):
            data[mcl] += ['']

    if n_keys != len(data.keys()):
        print('Incongruencia en cantidad de columas, ajustando.')
        columns = list(data.keys())
        del content, metadata, iterator, first_row, data, n_keys
        return load(path, columns)

    return data


def format_csv(cell: str):
    """ Apply the csv special character notation """
    # check `"`
    cell = cell.replace('"', '""')
    # check `,`
    return f'"{cell}"' if ',' in cell else cell


def build_csv(data):
    """ Build and save the final csv file """
    data_columns = tuple(data.keys())
    length = len(data[data_columns[0]])
    csv_array = [''] * (length + 1)

    # header
    print('Convirtiendo a csv.')
    for col in data_columns:
        csv_array[0] += format_csv(col) + ','
    csv_array[0] = csv_array[0][:-1]

    index = 0
    while index < length:
        for col in data_columns:
            csv_array[index + 1] += format_csv(data[col][index]) + ','

        csv_array[index + 1] = csv_array[index + 1][:-1]
        index += 1

    with open(output_path, 'wt', encoding='latin-1') as ofile:
        ofile.write('\n'.join(csv_array))

    print(f'File "{output_path}" generated.')


if __name__ == '__main__':
    args = parser.parse_args()
    file_path = args.file
    output_path = args.ofile

    file_data = load(file_path)
    lengths = list(map(
            lambda e: len(file_data[e]),
            file_data.keys()))

    assert max(lengths) == min(lengths), 'Algo anda mal con las columnas'

    build_csv(file_data)
