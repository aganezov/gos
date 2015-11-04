import sys
import os

ORIGINAL_REPEATS_FILES = [
    "/Users/aganezov/Documents/gwu/cbi/data/opossum/monDom5.fa.out",
    "/Users/aganezov/Documents/gwu/cbi/data/cat/felCat5.fa.out",
    "/Users/aganezov/Documents/gwu/cbi/data/dog/canFam3.fa.out",
    "/Users/aganezov/Documents/gwu/cbi/data/chimpanzee/panTro4.fa.out"
]
THRESHOLD_IDENTITY = 95
CLASSES = ["DNA", "LINE", "SINE"]

if __name__ == '__main__':
    for ORIGINAL_REPEATS_FILE in ORIGINAL_REPEATS_FILES:
        print("processing", os.path.basename(ORIGINAL_REPEATS_FILE))
        for THRESHOLD_LENGTH in range(400, 2100, 400):
            print("\tprocessing threshold", THRESHOLD_LENGTH)
            once = {}
            twice = {}

            with open(ORIGINAL_REPEATS_FILE, 'r') as file:
                for line in file.readlines():
                    blocks = line.split()
                    if len(blocks) > 0 and blocks[0] != "SW" and blocks[0] != "score":
                        repeat_class = blocks[10].split("/")[0]
                        repeat_length = int(blocks[6]) - int(blocks[5])
                        repeat_identity = 100 - (float(blocks[1]) + float(blocks[2]) + float(blocks[3]))
                        if repeat_class not in CLASSES or repeat_length < THRESHOLD_LENGTH or repeat_identity < THRESHOLD_IDENTITY:
                            continue
                        repeat = blocks[9]
                        if repeat in once:
                            twice[repeat] = True
                        else:
                            once[repeat] = True

            with open(ORIGINAL_REPEATS_FILE, 'r') as file:
                file_dir = os.path.join(os.path.dirname(ORIGINAL_REPEATS_FILE), "filtered_repeats")
                if not os.path.exists(file_dir):
                    os.mkdir(file_dir)
                filename = str(THRESHOLD_IDENTITY) + "_" + str(THRESHOLD_LENGTH) + ".txt"
                with open(os.path.join(file_dir, filename), 'w') as out:
                    for line in file.readlines():
                        blocks = line.split()
                        if len(blocks) > 0 and blocks[0] != "SW" and blocks[0] != "score":
                            repeat_class = blocks[10].split("/")[0]
                            repeat_length = int(blocks[6]) - int(blocks[5])
                            repeat_identity = 100 - (float(blocks[1]) + float(blocks[2]) + float(blocks[3]))
                            if repeat_class not in CLASSES or repeat_length < THRESHOLD_LENGTH or repeat_identity < THRESHOLD_IDENTITY:
                                continue
                            repeat = blocks[9]
                            if repeat in twice:
                                out.write(line)



