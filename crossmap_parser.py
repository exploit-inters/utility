'''
A script to parse crossmap.py results for SV project
'''
import sys
import argparse
# import ipdb
import copy


class Region:
    def __init__(self):
        self.frags = []

    def start_line(self, line):
        list = line.split()
        self.from_chr = list[0]
        self.from_start = int(list[1])
        self.from_end = int(list[2])
        self.from_summit = int(list[3])
        self.from_signal = float(list[4])
        self.from_strand = list[5]
        self.frags = []
        frag = Frag(line)
        self.frags.append(frag)

    def summit_frag_list(self):  # Return a list of all frags with summit (theoratically should only be one)
        return [x for x in self.frags if x.from_chr == self.from_chr and x.from_start <= self.from_summit and x.from_end >= self.from_summit]


class Frag:
    def __init__(self, line):
        list = line.split()
        self.to_chr = list[7]
        self.to_start = int(list[8])
        self.to_end = int(list[9])
        self.to_strand = list[12]
        if list[6] == '->':
            self.from_chr = list[0]
            self.from_start = int(list[1])
            self.from_end = int(list[2])
            self.from_strand = list[5]
        else:
            from_frag_list = list[6].strip('()').split(":")
            self.from_chr = from_frag_list[1]
            self.from_start = int(from_frag_list[2])
            self.from_end = int(from_frag_list[3])
            self.from_strand = from_frag_list[4]

    def merge_frags(self, frag):
        self.from_start = min(self.from_start, frag.from_start)
        self.from_end = max(self.from_end, frag.from_end)
        self.to_start = min(self.to_start, frag.to_start)
        self.to_end = max(self.to_end, frag.to_end)


def can_merge(frag1, frag2, distance):
    return (frag1.from_chr == frag2.from_chr and
            frag1.from_strand == frag2.from_strand and
            abs(max(frag1.from_start, frag2.from_start) - min(frag1.from_end, frag2.from_end) < distance) and
            frag1.to_chr == frag2.to_chr and
            frag1.to_strand == frag2.to_strand and
            abs(max(frag1.to_start, frag2.to_start) - min(frag1.to_end, frag2.to_end)) < distance)


def _get_args():
    parser = argparse.ArgumentParser(description='simple arguments')
    parser.add_argument(
        '--input',
        '-i',
        action="store",
        dest="input",
        help='The input crossmap output file.',
    )
    parser.add_argument(
        '--distance',
        '-d',
        action="store",
        dest="distance",
        default=50,
        help='The distance used to combine small indels into a large region. Default is 50bp',
    )
    return parser.parse_args()


def main():
    args = _get_args()
    with open(args.input, 'r') as Fh:
        regions = []
        last_region = Region()
        for line in Fh:
            line = line.rstrip()
            split = line.split()[6]
            if split != 'Fail':
                if split == '->' or split.startswith('(split.1:'):
                    if len(last_region.frags) > 0:
                        regions.append(copy.deepcopy(last_region))
                    last_region.start_line(line)
                else:
                    frag = Frag(line)
                    if can_merge(last_region.frags[-1], frag, args.distance):
                        last_region.frags[-1].merge_frags(frag)
                    else:
                        last_region.frags.append(frag)

    for region in regions:
        for frag in region.frags:
            print("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" %
                  (region.from_chr, region.from_start, region.from_end, region.from_strand, region.from_summit, region.from_signal,
                   frag.from_chr, frag.from_start, frag.from_end, frag.from_strand,
                   frag.to_chr, frag.to_start, frag.to_end, frag.to_strand))


if __name__ == "__main__":
    main()