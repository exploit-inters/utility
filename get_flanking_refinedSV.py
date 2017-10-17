import refine_calledSV

SIZE = 50  # the size differential cut off used to filter if there is a sv in flanking region.


def main():
    # the input refinedSV file should be 0 based bed file
    args = refine_calledSV._get_args()
    distance = args.distance
    target_size_dict = get_chrom_size(args.target_size)
    query_size_dict = get_chrom_size(args.query_size)
    with open(args.sv, 'r') as Fh:
        for line in Fh:
            line = line.rstrip()
            linelist = line.split()
            target_chr = linelist[0]
            target_start = linelist[1]
            target_end = linelist[2]
            query_chr = linelist[7]
            query_start = linelist[8]
            query_end = linelist[9]
            target_size = target_size_dict.get(target_chr)
            query_size = query_size_dict.get(query_chr)
            target_start_flanking = target_start - distance if target_start > distance else 0
            target_end_flanking = target_end + distance if target_end + distance < target_size else target_size
            query_start_flanking = query_start - distance if query_start > distance else 0
            query_end_flanking = query_end + distance if query_end + distance < query_size else query_size
            aln_start_flanking, aln_end_flanking = refine_calledSV.get_query(args.bam, target_chr, target_start_flanking, target_end_flanking)
            if abs(aln_start_flanking - query_start_flanking) < SIZE and abs(aln_end_flanking - query_end_flanking) < SIZE:
                print("%s\t%d\t%d\t%d\t%d" % (line, target_start_flanking, target_end_flanking, aln_start_flanking, aln_end_flanking))
            else:
                print("Maybe a SV in flanking region?\n%s\t%d\t%d\t%d\t%d" % (line, target_start_flanking, target_end_flanking, aln_start_flanking, aln_end_flanking))


def get_chrom_size(chrom_size):
    size_dict = dict()
    with open(chrom_size, 'r') as Fh:
        for line in Fh:
            line = line.rstrip()
            chrom, size = line.split()
            size_dict.update({chrom: size})
    return size_dict