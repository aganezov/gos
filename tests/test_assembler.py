import logging
from gos.exceptions import GOSIOError
import tempfile
import os
import unittest
import shutil
from gos.assembler import AssemblyManager
from gos.configuration import Configuration
from tests.test_logging import MockingLoggingHandler

__author__ = 'aganezov'

LOGGING_INFO = 'INFO'
LOGGING_DEBUG = 'DEBUG'
LOGGING_ERROR = 'ERROR'
LOGGING_CRITICAL = 'CRITICAL'


class AssemblerManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.input_dir = 'input'
        self.config = Configuration()
        self.output_dir_name = self.config[Configuration.OUTPUT][Configuration.OUTPUT_DIRECTORY]
        if not os.path.exists(self.output_dir_name):
            os.mkdir(self.output_dir_name)
        if not os.path.exists(self.input_dir):
            os.mkdir(self.input_dir)

        self.logger = logging.getLogger(self.config[Configuration.LOGGING][Configuration.LOGGER_NAME])
        self.logger.setLevel(level=logging.DEBUG)
        self.mocking_handler = MockingLoggingHandler(level=logging.DEBUG)
        self.mocking_handler.setFormatter(logging.Formatter(self.config[Configuration.LOGGING][Configuration.LOGGING_FORMAT]))
        self.mocking_handler.reset()
        self.logger.addHandler(self.mocking_handler)
        self.assembler_manager = AssemblyManager(logger=self.logger, apply_configuration_to_logger=False)
        self.mocking_handler.reset()

    def tearDown(self):
        if os.path.exists(self.output_dir_name):
            shutil.rmtree(self.output_dir_name)
        if os.path.exists(self.input_dir):
            shutil.rmtree(self.input_dir)
        self.mocking_handler.reset()

    def test_fields_on_initialization(self):
        manager = AssemblyManager()
        self.assertIsNotNone(manager.config)
        self.assertIsNotNone(manager.logger)
        self.assertIsNone(manager.breakpoint_graph)
        self.assertIsNone(manager.phylogenetic_tree)
        self.assertIsNone(manager.target_organisms)
        self.assertIsNone(manager.fragments_data)

    def test_logging_on_initialization(self):
        self.mocking_handler.reset()
        AssemblyManager(logger=self.logger)
        self.assertEqual(len(self.mocking_handler.messages[LOGGING_INFO]), 1)

    def test_default_logger_name(self):
        self.assertEqual(self.assembler_manager.logger.name,
                         self.assembler_manager.config[Configuration.LOGGING][Configuration.LOGGER_NAME])

    def test_logger_format(self):
        assembler_manager = AssemblyManager(configuration=self.config, logger=self.logger, apply_configuration_to_logger=True)
        self.assertEqual(assembler_manager.logger.level,
                         assembler_manager.config[Configuration.LOGGING][Configuration.LOGGING_LEVEL])

    def test_read_breakpoint_graph_data_no_edge_merge_io_good(self):
        tmp_files = self.assign_temp_genome_files_into_config()
        self.assembler_manager.config[Configuration.INPUT][Configuration.GENOMES][Configuration.MERGE_EDGES] = False
        try:
            self.assembler_manager.read_gene_order_data()
        finally:
            self.close_tmp_files(tmp_files)
        self.assertIsNotNone(self.assembler_manager.breakpoint_graph)
        self.assertEqual(len(list(self.assembler_manager.breakpoint_graph.nodes())), 31)
        self.assertEqual(len(list(self.assembler_manager.breakpoint_graph.edges())), 36)

    def close_tmp_files(self, tmp_files):
        for file in tmp_files:
            file.close()

    def test_read_breakpoint_graph_data_with_edge_merge_io_good(self):
        tmp_files = self.assign_temp_genome_files_into_config()
        self.assembler_manager.config[Configuration.INPUT][Configuration.GENOMES][Configuration.MERGE_EDGES] = True
        try:
            self.assembler_manager.read_gene_order_data()
        finally:
            self.close_tmp_files(tmp_files)
        self.assertIsNotNone(self.assembler_manager.breakpoint_graph)
        self.assertEqual(len(list(self.assembler_manager.breakpoint_graph.nodes())), 31)  # 18 regular nodes + 13 infinity nodes
        self.assertEqual(len(list(self.assembler_manager.breakpoint_graph.edges())), 30)

    def test_logging_read_breakpoint_graph_good_io(self):
        tmp_files = self.assign_temp_genome_files_into_config()
        self.assembler_manager.config[Configuration.INPUT][Configuration.GENOMES][Configuration.MERGE_EDGES] = False
        try:
            self.assembler_manager.read_gene_order_data()
        finally:
            self.close_tmp_files(tmp_files)
        self.assertEqual(len(self.mocking_handler.messages[LOGGING_INFO]), 3)  # single entry for every file processing
        self.assertEqual(len(self.mocking_handler.messages[LOGGING_DEBUG]), 3)  # indication of start + info about edges merge
        self.assertEqual(len(self.mocking_handler.messages[LOGGING_ERROR]), 0)  # io shall be good and data shall be good
        self.assertEqual(len(self.mocking_handler.messages[LOGGING_CRITICAL]), 0)  # nothing critical shall have happened

    def test_logging_read_breakpoint_graph_bad_file_silent_fail(self):
        tmp_files = self.assign_temp_genome_files_into_config()
        self.assembler_manager.config[Configuration.INPUT][Configuration.GENOMES][Configuration.IO_SILENT_FAIL] = True
        self.assembler_manager.config[Configuration.INPUT][Configuration.GENOMES][Configuration.SOURCE_FILES].append("bad_file_name")
        try:
            self.assembler_manager.read_gene_order_data()
        finally:
            self.close_tmp_files(tmp_files)
        self.assertEqual(len(self.mocking_handler.messages[LOGGING_ERROR]), 1)  # error of non existing file
        self.assertEqual(len(self.mocking_handler.messages[LOGGING_CRITICAL]), 0)  # silent fail is executed an application continues

    def test_logging_read_breakpoint_graph_bad_file_no_silent_fail(self):
        tmp_files = self.assign_temp_genome_files_into_config()
        self.assembler_manager.config[Configuration.INPUT][Configuration.GENOMES][Configuration.IO_SILENT_FAIL] = False
        self.assembler_manager.config[Configuration.INPUT][Configuration.GENOMES][Configuration.SOURCE_FILES].append("bad_file_name")
        try:
            with self.assertRaises(GOSIOError):
                self.assembler_manager.read_gene_order_data()
        finally:
            self.close_tmp_files(tmp_files)
        self.assertEqual(len(self.mocking_handler.messages[LOGGING_ERROR]), 1)  # error of non existing file
        self.assertEqual(len(self.mocking_handler.messages[LOGGING_CRITICAL]), 1)
        # silent fail is not executed and application raises exception and logs it

    def test_logging_read_breakpoint_graph_bad_data_silent_fail(self):
        tmp_files = self.create_temp_genome_files()
        self.add_bad_grimm_data_file(tmp_files)
        self.assembler_manager.config[Configuration.INPUT][Configuration.GENOMES][Configuration.SOURCE_FILES] = [tmp_file.name for tmp_file in
                                                                                                                 tmp_files]
        self.assembler_manager.config[Configuration.INPUT][Configuration.GENOMES][Configuration.IO_SILENT_FAIL] = True
        try:
            self.assembler_manager.read_gene_order_data()
        finally:
            self.close_tmp_files(tmp_files)
        self.assertEqual(len(self.mocking_handler.messages[LOGGING_ERROR]), 1)  # encounter bad grimm format is logged
        self.assertEqual(len(self.mocking_handler.messages[LOGGING_CRITICAL]), 0)  # silent fail is executed and application continues

    def add_bad_grimm_data_file(self, tmp_files):
        bad_genome = ['>genome 4\n', '1 2 3 $\n', '4 5 - - -6$\n', '7 8 9 $\n']
        self.add_bad_data_file(bad_genome, tmp_files)

    def add_bad_data_file(self, data, tmp_files):
        tmp_bad_file = tempfile.NamedTemporaryFile(suffix='.grimm', dir=self.input_dir, delete=True, mode='w+t')
        tmp_bad_file.writelines(data)
        tmp_bad_file.flush()
        tmp_files.append(tmp_bad_file)

    def test_logging_read_breakpoint_graph_bad_data_no_silent_fail(self):
        tmp_files = self.create_temp_genome_files()
        self.add_bad_grimm_data_file(tmp_files)
        self.assembler_manager.config[Configuration.INPUT][Configuration.GENOMES][Configuration.SOURCE_FILES] = [tmp_file.name for tmp_file in
                                                                                                                 tmp_files]
        self.assembler_manager.config[Configuration.INPUT][Configuration.GENOMES][Configuration.IO_SILENT_FAIL] = False
        try:
            with self.assertRaises(GOSIOError):
                self.assembler_manager.read_gene_order_data()
        finally:
            self.close_tmp_files(tmp_files)
        self.assertEqual(len(self.mocking_handler.messages[LOGGING_ERROR]), 1)  # encounter bad grimm format is logged
        self.assertEqual(len(self.mocking_handler.messages[LOGGING_CRITICAL]), 1)  # silent fail is not executed and application raises an exception

    def assign_temp_genome_files_into_config(self):
        tmp_files = self.create_temp_genome_files()
        self.assembler_manager.config[Configuration.INPUT][Configuration.GENOMES][Configuration.SOURCE_FILES] = [tmp_file.name for tmp_file in
                                                                                                                 tmp_files]
        return tmp_files

    def create_temp_genome_files(self):
        tmp_files = [tempfile.NamedTemporaryFile(suffix='.grimm', dir=self.input_dir, delete=True, mode='w+t') for _ in range(3)]
        genome_1 = ['>genome_1\n', '1 2 3 $\n', '4 5 6 $\n', '7 8 9 $\n']
        genome_2 = ['>genome 2\n', '3 2 1 $\n', '6 5 4 $\n', '9 8 7 $\n']
        genome_3 = ['>genome 3\n', '-2 -3 1 $\n', '4 -5 6 $\n', '9 -8 7 $\n']
        for file, genome_data in zip(tmp_files, [genome_1, genome_2, genome_3]):
            try:
                file.writelines(genome_data)
                file.flush()
            except IOError:
                raise AssertionError("Was unable to write genome data to temporary files")
        return tmp_files

    def test_read_phylogenetic_tree_good_io(self):
        tmp_files = self.create_temp_tree_files()
        self.assign_temp_tree_files_into_config(tmp_files)
        try:
            self.assembler_manager.read_phylogenetic_trees_data()
        finally:
            self.close_tmp_files(tmp_files)
        self.assertIsNotNone(self.assembler_manager.phylogenetic_tree)
        self.assertEqual(len(list(self.assembler_manager.phylogenetic_tree.nodes())), 7)
        self.assertEqual(len(list(self.assembler_manager.phylogenetic_tree.edges())), 6)
        self.assertTrue(self.assembler_manager.phylogenetic_tree.is_valid_tree)

    def assign_temp_tree_files_into_config(self, tmp_files):
        self.assembler_manager.config[Configuration.INPUT][Configuration.TREE][Configuration.SOURCE_FILES] = [tmp_file.name for tmp_file in tmp_files]

    def create_temp_tree_files(self):
        tmp_files = [tempfile.NamedTemporaryFile(suffix=".newick", mode="wt", dir=self.input_dir, delete=True) for _ in range(2)]
        tree_1 = ['((A)C,(E)D)Z;']
        tree_2 = ['((B)C,(F)D)Z;']
        for file, tree_data in zip(tmp_files, [tree_1, tree_2]):
            try:
                file.writelines(tree_data)
                file.flush()
            except IOError:
                raise AssertionError('Was unable to write test data into file containing tree information')
        return tmp_files

    def test_logging_read_phylogenetic_tree_good_io(self):
        tmp_files = self.create_temp_tree_files()
        self.assign_temp_tree_files_into_config(tmp_files=tmp_files)
        try:
            self.assembler_manager.read_phylogenetic_trees_data()
        finally:
            self.close_tmp_files(tmp_files=tmp_files)
        self.assertEqual(len(self.mocking_handler.messages[LOGGING_INFO]), 2)
        self.assertEqual(len(self.mocking_handler.messages[LOGGING_DEBUG]), 3)
        self.assertEqual(len(self.mocking_handler.messages[LOGGING_CRITICAL]), 0)
        self.assertEqual(len(self.mocking_handler.messages[LOGGING_ERROR]), 0)

    def test_logging_read_phylogenetic_tree_bad_file_silent_fail(self):
        tmp_files = self.create_temp_tree_files()
        self.assign_temp_tree_files_into_config(tmp_files=tmp_files)
        self.assembler_manager.config[Configuration.INPUT][Configuration.TREE][Configuration.SOURCE_FILES].append('bad_tree_file.newick')
        self.assembler_manager.config[Configuration.INPUT][Configuration.TREE][Configuration.IO_SILENT_FAIL] = True
        try:
            self.assembler_manager.read_phylogenetic_trees_data()
        finally:
            self.close_tmp_files(tmp_files)
        self.assertEqual(len(self.mocking_handler.messages[LOGGING_ERROR]), 1)
        self.assertEqual(len(self.mocking_handler.messages[LOGGING_CRITICAL]), 0)

    def test_read_phylogenetic_tree_bad_file_no_silent_fail(self):
        pass

    def test_logging_read_phylogenetic_tree_bad_data_silent_fail_valid_tree(self):
        tmp_files = self.create_temp_tree_files()
        self.add_bad_tree_data_file(tmp_files=tmp_files)
        self.assign_temp_tree_files_into_config(tmp_files=tmp_files)
        self.assembler_manager.config[Configuration.INPUT][Configuration.TREE][Configuration.IO_SILENT_FAIL] = True
        try:
            self.assembler_manager.read_phylogenetic_trees_data()
        finally:
            self.close_tmp_files(tmp_files)
        self.assertEqual(len(self.mocking_handler.messages[LOGGING_ERROR]), 1)
        self.assertEqual(len(self.mocking_handler.messages[LOGGING_CRITICAL]), 0)
        self.assertTrue(self.assembler_manager.phylogenetic_tree.is_valid_tree)

    def add_bad_tree_data_file(self, tmp_files):
        bad_tree = ['a,,b']
        self.add_bad_data_file(bad_tree, tmp_files=tmp_files)


if __name__ == '__main__':
    unittest.main()
