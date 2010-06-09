from osm4routing import *
from progressbar import ProgressBar
import os
import bz2, gzip
import sys
from optparse import OptionParser


def parse(file, outformat="csv", edges_name="edges", nodes_name="nodes", conn = ""):

    if not os.path.exists(file):
        sys.stderr.write("File {0} doesn't exist\n".format(file))
        sys.exit(1)

    extension = os.path.splitext(file)[1]
    if extension == '.bz2':
        print "Recognized as bzip2 file"
        f = bz2.BZ2File(file, 'r') 

    elif extension == '.gz':
        print "Recognized as gzip2 file"
        f = gzip.open(file, 'r') 

    else:
        print "Supposing OSM/xml file"
        filesize = os.path.getsize(file)
        f = open(file, 'r') 

    buffer_size = 4096
    p = Parser()
    eof = False
    print "Step 1: reading file {0}".format(file)
    read = 0
    while not eof:
        s = f.read(buffer_size)
        eof = len(s) != buffer_size
        p.read(s, len(s), eof)
        read += len(s)

    print "  Read {0} nodes and {1} ways\n".format(p.get_osm_nodes(), p.get_osm_ways())

    print "Step 2: saving the nodes"
    nodes = p.get_nodes()
    if outformat == "csv":
        n = open(nodes_name + '.csv', 'w')
        n.write('"node_id","longitude","latitude"\n')
    pbar = ProgressBar(maxval=len(nodes))
    count = 0
    for node in nodes:
        if outformat == "csv":
            n.write("{0},{1},{2}\n".format(node.id, node.lon, node.lat))
        count += 1
        pbar.update(count)
    n.close()
    pbar.finish()

    print "  Wrote {0} nodes\n".format(count)

    print "Step 3: saving the edges"
    edges = p.get_edges()
    pbar = ProgressBar(maxval=len(edges))
    count = 0
    if outformat == "csv":
        e = open(edges_name + '.csv', 'w')
        e.write('"edge_id","source","target","length","car","car reverse","bike","bike reverse","foot","WKT"\n')
    for edge in edges:
        if outformat == "csv":
            e.write('{0},{1},{2},{3},{4},{5},{6},{7},{8},LINESTRING("{9}")\n'.format(edge.edge_id, edge.source, edge.target, edge.length, edge.car, edge.car_d, edge.bike, edge.bike_d, edge.foot, edge.geom))
        count += 1
        pbar.update(count)
    e.close()
    pbar.finish()
    print "  Wrote {0} edges\n".format(count)

    print "Happy routing :) and please give some feedback!"

def main():
    usage = """Usage: %prog [options] input_file

input_file must be an OSM/XML file. It can be compressed with gzip (.gz) or bzip2 (.bz2)"""


    parser = OptionParser(usage)
    parser.add_option("-o", "--out_format", dest="out_format", default="csv", help="Output format [default: %default]")
    parser.add_option("-n", "--nodes_name", dest="nodes_name", default="nodes", help="Name of the file or table where nodes are stored [default: %default]")
    parser.add_option("-e", "--edges_name", dest="edges_name", default="edges", help="Name of the file or table where edges are stored [default: %default]")
    parser.add_option("-d", "--db_params", dest="database_parameters", help="Parameters to connect to the database")
    (options, args) = parser.parse_args()

    if options.out_format != "csv" and not options.database_parameters:
        sys.stderr.write("Missing database parameter\n")
        sys.exit(1)
    if len(args) != 1:
        sys.stderr.write("Wrong number of argumented. Expected 1, got {0}\n".format(len(args)))
        sys.exit(1)

    parse(args[0], options.out_format, options.edges_name, options.nodes_name, options.database_parameters)

if __name__ == "__main__":
    main()