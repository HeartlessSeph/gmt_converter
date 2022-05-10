import argparse
import os
from read import read_file
from structure.bone import Bone, find_bone
from structure.curve import *
from structure.name import Name
from collections import OrderedDict
from structure.version import *
from util.dicts import *
from write import write_file

description = """
GMT Tool
By HeartlessSeph based on code by SutandoTsukai181
A subtool of the GMT_Converter to edit animation data.
"""

epilog = """

"""

parser = argparse.ArgumentParser(
    description=description, epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('-i', '--inpath', action='store',
                    help='GMT input name (or input folder path)')
parser.add_argument('-copy', '--copy', action='store',
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
parser.add_argument('-fr', '--framecut', action='store',
                    help='Frames to cut')
parser.add_argument('-claw', '--claw', action='store_true',
                    help='Fix claw hands')
parser.add_argument('-rem_pos', '--rem_pos', action='store_true',
                    help='Removes non-essential translation')


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
            args.outpath = args.inpath[:-4] + f"-conv.gmt"
        if args.inpath.lower() == args.outpath.lower():
            print(
                "Error: Input path cannot be the same as output path when not using -d or -dr")
            os.system('pause')
            return -1

    return args


# def copy_curve(path1, path2, outpath):
#     in_file_1 = read_file(path1)
#     in_file_2 = read_file(path2)
#     dst_gmt = GMTProperties(GAME['y6'])
#
#     bones_to_copy = ["pattern_c_n"]
#
#     for anm in in_file_2.animations:
#         for bone in reversed(anm.bones):
#             if bone.name.string() in bones_to_copy:
#                 bone_1, bone_idx_1 = find_bone(bone.name.string(), in_file_1.animations[0].bones)
#                 bone_2, bone_idx_2 = find_bone(bone.name.string(), anm.bones)
#                 if bone_1:
#                     in_file_1.animations[0].bones[bone_idx_1] = deepcopy(bone)
#                 else:
#                     in_file_1.animations[0].bones.append(deepcopy(bone))
#                 print(bone.name.string() + " Updated")
#     with open(outpath, 'wb') as g:
#         g.write(write_file(in_file_1, dst_gmt.version))
#         print("Converted " + outpath)


def option_select(option_dict, message):
    """

    :param option_dict: Dict Object
    :param message: String
    """
    print(message)
    for key, value in option_dict.items():
        print(str(key) + ": " + value)
    print("")
    game_num = int(input('Input a number: '))
    x = 0
    while x == 0:
        if game_num in option_dict:
            print("")
            return game_num
        else:
            print("Given number is not in listed range")
            game_num = int(input('Input a number: '))


def select_bone(bones):
    if len(bones) == 0:
        raise Exception("No bones in animation?")
    for b_idx, bone in enumerate(bones):
        print(str(b_idx) + ":" + bone.name.string())
        last_b_idx = b_idx
    print("")
    my_b_idx = int(input("Select bone by bone ID: "))
    while my_b_idx > last_b_idx or not isinstance(my_b_idx, int):
        my_b_idx = int(input("Bone ID out of range. Please select a valid bone ID: "))
    print(str(bones[my_b_idx].name.string()) + " selected.")
    return my_b_idx


def add_bone(bones):
    bone_to_add = input("Please enter the name of the bone you want to add: ")
    act_bone = [b for b in bones if bone_to_add == b.name.string()]
    if len(act_bone):
        print("Bone already present in bones list")
        return bones
    new_bone = Bone()
    new_bone.name = Name(bone_to_add)
    bones.append(new_bone)
    print(bone_to_add + " added to bone list")
    return bones


def remove_bone(bones):
    act_bone = select_bone(bones)
    bones.pop(act_bone)
    print(bones[act_bone] + " removed from bones list.")
    return bones


def select_curve(curves):
    if len(curves) == 0:
        print("No curves present in bone.")
        return -1
    for c_idx, curve in enumerate(curves):
        print(str(c_idx) + ":" + curve.curve_format.name)
        last_c_idx = c_idx
    print("")
    my_c_idx = int(input("Select curve by curve ID: "))
    while my_c_idx > last_c_idx:
        my_c_idx = int(input("Curve ID out of range. Please select a valid curve ID: "))
    return my_c_idx


def add_curve(curves):
    new = generate_curve()
    curves.append(new)
    return curves


def remove_curve(curves):
    act_curve = select_curve(curves)
    if act_curve != -1:
        curves.pop(act_curve)
    return curves


def select_frame(curve):
    for f_idx, frame in enumerate(curve.graph.keyframes):
        print(str(f_idx) + " (Frame " + str(frame) + "): " + str(curve.values[f_idx]))
        last_f_idx = f_idx
    print("")
    my_f_idx = int(input("Select frame by frame ID: "))
    while my_f_idx > last_f_idx:
        my_f_idx = int(input("Frame ID out of range. Please select a valid frame ID: "))
    return my_f_idx


def add_frame(curve):
    for f_idx, frame in enumerate(curve.graph.keyframes): print("Frame " + str(frame) + ": " + str(curve.values[f_idx]))
    my_frame = int(input("Enter frame to input value: "))
    if my_frame in curve.graph.keyframes:
        my_frame = int(input("Frame already present. Please select a different value: "))
    my_values_amount = int(input("Enter amount of elements in values list: "))
    for frame_idx, frame in reversed(list(enumerate(curve.graph.keyframes))):
        if my_frame > frame:
            curve.graph.keyframes.insert(frame_idx + 1, my_frame)
            temp_array = []
            for i in range(my_values_amount): temp_array.append(0)
            curve.values.insert(frame_idx + 1, temp_array)
            break
    return curve


def remove_frame(curve):
    act_curve = select_frame(curve)
    if act_curve != -1:
        curve.values.pop(act_curve)
        curve.graph.keyframes.pop(act_curve)
    return curve


def select_value_type():
    value_types = ["Float", "Int"]
    last_idx = len(value_types) - 1
    for type_idx, val_type in enumerate(value_types): print(str(type_idx) + ": " + str(val_type))
    print("")
    my_idx = int(input("Select type: "))
    while my_idx > last_idx:
        my_idx = int(input("Type not in list, select valid type: "))
    return value_types[my_idx]


def edit_curve_value(curve_vals):
    print(curve_vals)
    for curve_idx, value in enumerate(curve_vals):
        print("Current curve value: " + str(curve_vals[curve_idx]))
        print("Current curve value type = " + str(type(curve_vals[curve_idx])))
        my_value = input("Enter new value or leave blank and press enter to go to next curve value: ")
        if my_value == "": continue
        my_type = select_value_type()
        if my_type == "Float": curve_vals[curve_idx] = float(my_value)
        if my_type == "Int": curve_vals[curve_idx] = int(my_value)
    return curve_vals


def edit_all_frames(curve):
    for f_idx, frame in enumerate(curve.graph.keyframes): print("Frame " + str(frame) + ": " + str(curve.values[f_idx]))
    num_vals = len(curve.values[0])
    update_list = []
    value_type = select_value_type()
    print(value_type)
    for i in range(num_vals):
        temp_val = input("Amount to change for number " + str(i + 1) + ": ")
        if value_type == "Int":
            update_list.append(int(temp_val))
        elif value_type == "Float":
            update_list.append(float(temp_val))

    for frame_idx, frame in enumerate(curve.values):
        for i in range(num_vals):
            curve.values[frame_idx][i] += update_list[i]
    return curve


def select_game_version(ver_dict):
    last_idx = len(ver_dict) - 1
    for ver_idx, version in enumerate(list(ver_dict.values())):
        print(str(ver_idx) + " " + version)
    print("")
    my_idx = int(input("Select game: "))
    while my_idx > last_idx:
        my_idx = int(input("Game ID not in list, select valid version: "))
    return list(ver_dict.keys())[my_idx]


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


def pos_fix(path, outpath):
    in_file = read_file(path)
    dst_gmt = GMTProperties(GAME[select_game_version(GAME)])
    exclude_list = ["center_c_n", "vector_c_n", "center_n", "sync_c_n"]

    for anm in in_file.animations:
        for bone in anm.bones:
            for curve_idx, curve in reversed(list(enumerate(bone.curves))):
                curve.neutralize()
                if len(curve.values) > 0:
                    if 'POS' in curve.curve_format.name:
                        if bone.name.string() not in exclude_list: bone.curves.pop(curve_idx)
        for bone_idx, bone in reversed(list(enumerate(anm.bones))):
            if "phy" in bone.name.string() or "twist" in bone.name.string(): anm.bones.pop(bone_idx)
    with open(outpath, 'wb') as g:
        g.write(write_file(in_file, dst_gmt.version))
        print("Converted " + outpath)


def remove_frames_start(path1, frame_start, outpath):
    in_file = read_file(path1)
    dst_gmt = GMTProperties(GAME[select_game_version(GAME)])
    bones_to_remove = []

    for anm in in_file.animations:
        for bone in anm.bones:
            bone.blend_pos_curves()
            bone.blend_rot_curves()
            for curve in bone.curves:
                if len(curve.values) > 0:
                    if len(curve.graph.keyframes) != 1:
                        if curve.graph.keyframes[-1] < frame_start:
                            curve.graph.keyframes = [curve.graph.keyframes[-1] - curve.graph.keyframes[-1]]
                            curve.values = [curve.values[-1]]
                        else:
                            for idx, frame in reversed(list(enumerate(curve.graph.keyframes))):
                                if frame < frame_start:
                                    curve.graph.keyframes.pop(idx)
                                    curve.values.pop(idx)
                                else:
                                    curve.graph.keyframes[idx] = frame - frame_start
                            if len(curve.graph.keyframes) == 0:
                                bones_to_remove.append(bone.name.string())
                    else:
                        if curve.graph.keyframes[0] < frame_start:
                            curve.graph.keyframes[0] = curve.graph.keyframes[0] - curve.graph.keyframes[0]
                        else:
                            curve.graph.keyframes[0] = curve.graph.keyframes[0] - frame_start
    bones_to_remove = list(OrderedDict.fromkeys(bones_to_remove))
    for bone in bones_to_remove:
        _, bone_idx = find_bone(bone, in_file.animations[0].bones)
        in_file.animations[0].bones.pop(bone_idx)

    for anm in in_file.animations:
        vector, vector_idx = find_bone("vector", anm.bones)
        sync, sync_idx = find_bone("sync", anm.bones)
        conf = 0
        if vector:
            for curve in anm.bones[vector_idx].curves:
                curve.neutralize()
                if curve.curve_format == CurveFormat.POS_VEC3:
                    conf = 1
                    c_subtract_0 = curve.values[0][0]
                    c_subtract_1 = curve.values[0][1]
                    c_subtract_2 = curve.values[0][2]
                    for value in curve.values:
                        value[0] = value[0] - c_subtract_0
                        value[1] = value[1] - c_subtract_1
                        value[2] = value[2] - c_subtract_2
            if sync:
                for curve in anm.bones[sync_idx].curves:
                    curve.neutralize()
                    if curve.curve_format == CurveFormat.POS_VEC3:
                        if conf == 1:
                            for value in curve.values:
                                value[0] = value[0] - c_subtract_0
                                value[1] = value[1] - c_subtract_1
                                value[2] = value[2] - c_subtract_2
    with open(outpath, 'wb') as g:
        g.write(write_file(in_file, dst_gmt.version))
        print("Converted " + outpath)


def remove_frames_end(path1, frame_end, outpath):
    in_file = read_file(path1)
    dst_gmt = GMTProperties(GAME[select_game_version(GAME)])
    bones_to_remove = []

    for anm in in_file.animations:
        for bone in anm.bones:
            for curve in bone.curves:
                if len(curve.values) > 0:
                    if len(curve.graph.keyframes) != 1:
                        for idx, frame in reversed(list(enumerate(curve.graph.keyframes))):
                            if frame > frame_end:
                                curve.graph.keyframes.pop(idx)
                                curve.values.pop(idx)
                        if len(curve.graph.keyframes) == 0:
                            bones_to_remove.append(bone.name.string())
    bones_to_remove = list(OrderedDict.fromkeys(bones_to_remove))
    for bone in bones_to_remove:
        _, bone_idx = find_bone(bone, in_file.animations[0].bones)
        in_file.animations[0].bones.pop(bone_idx)
    with open(outpath, 'wb') as g:
        g.write(write_file(in_file, dst_gmt.version))
        print("Converted " + outpath)


def Curve_Editor(path, outpath):
    in_file = read_file(path)
    dst_gmt = GMTProperties(GAME[select_game_version(GAME)])

    for anm_idx, anm in enumerate(in_file.animations):
        cancel_choice = ""
        while cancel_choice == "":
            bone_option = option_select({0: "Select Bone", 1: "Add Bone", 2: "Remove Bone"}, "Select an Option")
            if bone_option == 0:
                cur_bone = select_bone(in_file.animations[anm_idx].bones)
                curve_option = option_select({0: "Select Curve", 1: "Add Curve", 2: "Remove Curve"}, "Select an Option")
                if curve_option == 0:
                    cur_curve = select_curve(in_file.animations[anm_idx].bones[cur_bone].curves)
                    if cur_curve > -1:
                        value_option = option_select({0: "Select Value", 1: "Add Value", 2: "Remove Value", 3: "Edit all Frames"}, "Select an Option")
                        if value_option == 0:
                            cur_value = select_frame(in_file.animations[anm_idx].bones[cur_bone].curves[cur_curve])
                            cur_values = edit_curve_value(in_file.animations[anm_idx].bones[cur_bone].curves[cur_curve].values[cur_value])
                            in_file.animations[anm_idx].bones[cur_bone].curves[cur_curve].values[cur_value] = cur_values
                            print("Curve value updated!")
                        elif value_option == 1:
                            in_file.animations[anm_idx].bones[cur_bone].curves[cur_curve] = add_frame(in_file.animations[anm_idx].bones[cur_bone].curves[cur_curve])
                        elif value_option == 2:
                            in_file.animations[anm_idx].bones[cur_bone].curves[cur_curve] = remove_frame(in_file.animations[anm_idx].bones[cur_bone].curves[cur_curve])
                        elif value_option == 3:
                            in_file.animations[anm_idx].bones[cur_bone].curves[cur_curve] = edit_all_frames(in_file.animations[anm_idx].bones[cur_bone].curves[cur_curve])
                elif curve_option == 1:
                    in_file.animations[anm_idx].bones[cur_bone].curves = add_curve(in_file.animations[anm_idx].bones[cur_bone].curves)
                elif curve_option == 2:
                    in_file.animations[anm_idx].bones[cur_bone].curves = remove_curve(in_file.animations[anm_idx].bones[cur_bone].curves)
            elif bone_option == 1:
                in_file.animations[anm_idx].bones = add_bone(in_file.animations[anm_idx].bones)
            elif bone_option == 2:
                in_file.animations[anm_idx].bones = remove_bone(in_file.animations[anm_idx].bones)

            print("")
            cancel_choice = input("Press enter to continue editing or enter value to stop editing animation: ")

    with open(outpath, 'wb') as g:
        g.write(write_file(in_file, dst_gmt.version))
        print("Converted " + outpath)


def claw_check(args):
    if args.dir:
        for r, d, f in os.walk(args.inpath):
            for file in f:
                gmt_file = os.path.join(r, file)
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
        # if not args.inpath.startswith('\"'):
        #    args.inpath = f"\"{args.inpath}\""
        with open(args.outpath, 'wb') as g:
            g.write(fix_claw_hands(args.inpath))
            print(f"converted {args.outpath}")
    print("DONE")


def main():
    args = parser.parse_args()
    processed = process_args(args)
    if type(processed) is int:
        return processed
    args = processed

    if args.framecut:
        print("Press 1 to cut frames from beginning")
        print("Press 2 to cut frames from end")
        cut_type = int(input(""))
        if cut_type == 1: remove_frames_start(args.inpath, int(args.framecut), args.outpath)
        if cut_type == 2: remove_frames_end(args.inpath, int(args.framecut), args.outpath)

    elif args.claw:
        claw_check(args)

    elif args.rem_pos:
        pos_fix(args.inpath, args.outpath)

    else:
        Curve_Editor(args.inpath, args.outpath)


if __name__ == "__main__":
    main()
