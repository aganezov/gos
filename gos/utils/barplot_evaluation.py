# -*- coding: utf-8 -*-
from boomslang.Bar import Bar
from boomslang.ClusteredBars import ClusteredBars
from boomslang.Plot import Plot
from boomslang.StackedBars import StackedBars

import sys

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"

COLORS = ["green", "blue", "yellow", "cyan", "magenta", "black"]
LABELS = ["tool1", "tool2", "tool3", "tool4", "tool5", "tool6"]
SPACING = 0.5
PLOT_SAVE_FILENAME = "bar_plot_multitool_evaluation.pdf"


def barplot_evaluation(lines, x_ticks_labels,
                    y_label="%", x_label="Length of shortest removed repeat",
                    colors=COLORS, labels=LABELS,
                    file_name=PLOT_SAVE_FILENAME):

    # since each tool must be presented as a pair of lists, we check this explicitly
    assert len(text_lines[1:]) % 2 == 0

    data = []
    #
    # data is presented as list of pairs of lists:
    #   every pair of lists describes values for a single tool
    #   number of entries in each list corresponds to the number of x ticks
    #   first list corresponds to "true positive values" for respective tool
    #   second list corresponds to "false positive values" for respective tool
    #
    for tp, fp in zip(lines[1::2], lines[2::2]):
        data.append([[float(value) for value in tp.split()],
                     [float(value) for value in fp.split()]])
    cluster = ClusteredBars()
    for i in xrange(len(data)):
        stack = StackedBars()
        for j in xrange(2):
            bar = Bar()
            bar.xValues = range(len(x_ticks_labels))
            bar.yValues = data[i][j]
            bar.color = "red" if j % 2 == 1 else colors[i]  # all "false positive values" are colored red,
                                                            # while "true positives" change from tool to tool
            bar.label = labels[i]
            stack.add(bar)
        cluster.add(stack)

    cluster.spacing = SPACING
    cluster.xTickLabels = x_ticks_labels

    plot = Plot()
    plot.add(cluster)
    plot.xLabel = x_label
    plot.yLabel = y_label

    plot.save(file_name)


if __name__ == "__main__":
    data_file = sys.argv[1]
    plot_filename = sys.argv[2] if len(sys.argv) > 2 else PLOT_SAVE_FILENAME

    with open(data_file, "rt") as source:
        text_lines = source.readlines()
        # empty lines are removed from processing
        text_lines = [line.strip() for line in text_lines if len(line.strip()) > 0]
        # first line corresponds to x ticks labels
        text_x_ticks_labels = text_lines[0].split()

        barplot_evaluation(lines=text_lines, x_ticks_labels=text_x_ticks_labels)
