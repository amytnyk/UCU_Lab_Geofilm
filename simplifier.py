from random import sample
import argparse


def simplify(src: str, dst: str, lines_count: int):
    with open(src, 'r', encoding='iso-8859-1') as source_file:
        lines = source_file.read().split('\n')
        header_lines = lines[:lines.index("LOCATIONS LIST") + 2]
        selected_lines = sample(lines, lines_count)
        bottom_lines = lines[-2:]

        with open(dst, 'w', encoding='iso-8859-1') as dest_file:
            dest_file.write('\n'.join(header_lines + selected_lines + bottom_lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("src", help="source file path",
                        type=str)
    parser.add_argument("dst", help="destination file path",
                        type=str)
    parser.add_argument("lines", help="number of lines to choose",
                        type=int)
    args = parser.parse_args()
    simplify(args.src, args.dst, args.lines)


if __name__ == "__main__":
    main()
