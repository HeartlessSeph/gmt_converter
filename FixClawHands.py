import argparse
import os
import io
from typing import List

import math
from copy import deepcopy
from os.path import basename
from typing import List

from pyquaternion import Quaternion

from read import read_file
from structure.animation import Animation
from structure.bone import Bone, find_bone, find_bone_index
from structure.curve import *
from structure.file import GMTFile
from structure.graph import *
from structure.header import GMTHeader
from structure.name import Name
from structure.types.format import CurveFormat, curve_array_to_quat
from structure.version import *
from util.binary import BinaryReader
from util.dicts import *
from util.read_cmt import read_cmt_file
from util.read_gmd import (GMDBone, find_gmd_bone, get_face_bones, read_gmd_bones)
from util.write_cmt import write_cmt_file
from write import write_file

description = """
GMT Converter v0.5.4
By SutandoTsukai181, fork by HeartlessSeph
A subtool of the GMT_Converter to attempt to mitigate "Claw Hands".
Only works on Dragon Engine animations.
"""

epilog = """
EXAMPLE
Using the main GMT_Converter, first convert an animation to Dragon Engine.
Then simply run this program on that animation using the command line options:
    FixClawHands.exe -i animation_with_claws.gmt -o fixed_animation.gmt

If you want to fix an entire folder of GMTs, add the -d flag (or -dr to convert files in subfolders too):
    FixClawHands.exe -d -i folder_containing_gmts
"""

parser = argparse.ArgumentParser(
    description=description, epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('-i', '--inpath', action='store',
                    help='GMT input name (or input folder path)')
parser.add_argument('-o', '--outpath', action='store', help='GMT output name')

parser.add_argument('-d', '--dir', action='store_true',
                    help='the input is a dir')
parser.add_argument('-dr', '--recursive', action='store_true',
                    help='the input is a dir; recursively convert subfolders')
parser.add_argument('-ns', '--nosuffix', action='store_true',
                    help='do not add suffixes at the end of converted files')
parser.add_argument('-sf', '--safe', action='store_true',
                    help='ask before overwriting files')


def process_args(args):
    if not args.inpath:
        if os.path.isdir("input_folder"):
            args.dir = True
            args.inpath = "\"input_folder\""
        else:
            parser.print_usage()
            print("\nError: Provide an input path with -i or put the files in \"<gmt_converter_path>\\input_folder\\\"")
            os.system('pause')
            return -1

    if args.dir or args.recursive:
        args.dir = True
        if not args.outpath:
            args.outpath = "output_folder"
        if args.inpath.lower() == args.outpath.lower() and args.nosuffix:
            print(
                "Error: Input path cannot be the same as output path when using --nosuffix with -d or -dr")
            os.system('pause')
            return -1
    else:
        if not args.outpath:
            if args.nosuffix:
                print(
                    "Error: Provide an output path when using --nosuffix without -d or -dr")
                os.system('pause')
                return -1
            args.outpath = args.inpath[:-4] + f"-{args.outgame}.gmt"
        if args.inpath.lower() == args.outpath.lower():
            print(
                "Error: Input path cannot be the same as output path when not using -d or -dr")
            os.system('pause')
            return -1

    return args


def fix_claw_hands(path):
    in_file = read_file(path)
    dst_gmt = GMTProperties(GAME['y6'])

    for anm in in_file.animations:
        for bone in anm.bones:
            for curve_idx, curve in reversed(list(enumerate(bone.curves))):
                curve.neutralize()
                if len(curve.values) > 0:
                    if 'POS' in curve.curve_format.name:
                        if bone.name.string() in KIRYU_HAND: bone.curves.pop(curve_idx)
    return write_file(in_file, dst_gmt.version)


def main():
    args = parser.parse_args()
    processed = process_args(args)
    if type(processed) is int:
        return processed
    args = processed

    if args.dir:
        for r, d, f in os.walk(args.inpath):
            for file in f:
                gmt_file = os.path.join(r, file)
                # if not gmt_file.startswith('\"'):
                #    gmt_file = f"\"{gmt_file}\""
                if args.nosuffix:
                    output_file = os.path.join(args.outpath, file)
                else:
                    output_file = os.path.join(
                        args.outpath, file[:-4] + f"-fixed.gmt")

                if not gmt_file.endswith('.gmt'):
                    continue

                if args.safe and os.path.isfile(output_file):
                    print(
                        f"Output file \"{output_file}\" already exists. Overwrite? (select 's' to stop conversion)")
                    result = input("(y/n/s) ").lower()
                    if result != 'y':
                        if result == 's':
                            print("Stopping operation...")
                            os.system('pause')
                            return -1
                        print(f"Skipping \"{output_file}\"...")
                        continue
                with open(output_file, 'wb') as g:
                    g.write(fix_claw_hands(gmt_file))
                    print(f"converted {output_file}")
            if not args.recursive:
                break
    else:
        if args.safe and os.path.isfile(args.outpath):
            print(f"Output file \"{args.outpath}\" already exists. Overwrite?")
            result = input("(y/n) ").lower()
            if result != 'y':
                print("Stopping operation...")
                os.system('pause')
                return
        with open(args.outpath, 'wb') as g:
            g.write(fix_claw_hands(args.inpath))
            print(f"converted {args.outpath}")
    print("DONE")


if __name__ == "__main__":
    main()
