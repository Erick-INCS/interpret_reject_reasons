#!/usr/bin/env python3
""" This script reads and interprets the rejected reasons file """

import argparse

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



SPLIT_SIZE = 206


def interpret_row(row):
    """ Returns the data of single record """
    spl_size = SPLIT_SIZE
    return ','.join(list(map(format_csv, [
            e for i, e in enumerate(row[:spl_size])
            if i % 2 == 1
            ] + ['|'.join(row[spl_size+1:])])))


def interpret_header(row):
    """ Returns the header """
    spl_size = SPLIT_SIZE
    return list(map(format_csv, [
            e for i, e in enumerate(row[:spl_size])
            if i % 2 == 0
            ] + [row[spl_size]]))


def format_csv(cell: str):
    """ Apply the csv special character notation """
    # check `"`
    cell = cell.replace('"', '""')
    # check `,`
    return f'"{cell}"' if ',' in cell else cell


def load(path: str):
    """ Loads the data """

    with open(path, 'rt', encoding='latin-1') as file_stram:
        content = file_stram.readlines()

    content = list(filter(
            lambda l: l,
            map(lambda l: l.replace('\n', ''), content)))

    content = map(
        lambda l: l.split('|'),
        content)

    # Save metadata
    metadata = next(content)
    iterator = 0
    metadata_text = ''
    for val in metadata:
        val = val.strip()
        if val:
            if iterator % 2 == 0:
                metadata_text += val + ':\n' + ' ' * 4
            else:
                metadata_text += val + '\n'
        iterator += 1

    with open('rejectReasons_metadata.txt', 'wt') as mfile:
        mfile.write(metadata_text)

    # Construct file content
    first_row = next(content)

    columns = ','.join(map(
        lambda s: s.strip(),
        interpret_header(first_row)))
    frow = interpret_row(first_row)
    content = list(map(interpret_row, content))

    return columns +\
           '\n' +\
           frow +\
           '\n' +\
           '\n'.join(content)


if __name__ == '__main__':
    args = parser.parse_args()
    file_path = args.file
    output_path = args.ofile

    content = load(file_path)
    with open(output_path, 'wt', encoding='latin-1') as ofile:
        ofile.write(content)

    print(f'File "{output_path}" generated.')
