import unittest
from gos.configuration import Configuration

__author__ = 'aganezov'


class ConfigTestCase(unittest.TestCase):
    def test_empty_config_creation(self):
        config = Configuration()
        self.assertIsInstance(config, dict)

    def test_empty_configuration_structure(self):
        config = Configuration()
        # top level
        self.assertIn(Configuration.INPUT, config)
        self.assertIn(Configuration.LOGGING, config)
        self.assertIn(Configuration.OUTPUT, config)
        self.assertIn(Configuration.PROCESSING, config)

        # input configuration
        self.assertIn(Configuration.GENOMES, config[Configuration.INPUT])
        self.assertIn(Configuration.TREE, config[Configuration.INPUT])

        # input -> genomes configuration
        self.assertIn(Configuration.SOURCE_FILES, config[Configuration.INPUT][Configuration.GENOMES])
        self.assertIn(Configuration.MERGE_EDGES, config[Configuration.INPUT][Configuration.GENOMES])
        self.assertIn(Configuration.IO_SILENT_FAIL, config[Configuration.INPUT][Configuration.GENOMES])

        # input -> tree configuration
        self.assertIn(Configuration.SOURCE_FILES, config[Configuration.INPUT][Configuration.TREE])
        self.assertIn(Configuration.IO_SILENT_FAIL, config[Configuration.INPUT][Configuration.TREE])

        # logging configuration
        self.assertIn(Configuration.LOGGING_LEVEL, config[Configuration.LOGGING])
        self.assertIn(Configuration.LOGGING_FORMAT, config[Configuration.LOGGING])
        self.assertIn(Configuration.IO_SILENT_FAIL, config[Configuration.LOGGING])
        self.assertIn(Configuration.IO_DESTINATION, config[Configuration.LOGGING])
        self.assertIn(Configuration.ENABLE_IO_LOGGING, config[Configuration.LOGGING])
        self.assertIn(Configuration.BREAKPOINT_GRAPH_CONSTRUCTION, config[Configuration.LOGGING])
        self.assertIn(Configuration.ENABLE_BG_CONSTRUCTION_LOGGING, config[Configuration.LOGGING])
        self.assertIn(Configuration.TREE_PROCESSING, config[Configuration.LOGGING])
        self.assertIn(Configuration.ENABLE_TREE_PROCESSING_LOGGING, config[Configuration.LOGGING])
        self.assertIn(Configuration.ASSEMBLY_POINTS_IDENTIFICATION, config[Configuration.LOGGING])
        self.assertIn(Configuration.ENABLE_POINTS_IDENTIFICATION_LOGGING, config[Configuration.LOGGING])
        self.assertIn(Configuration.ASSEMBLY_POINTS_GLUING, config[Configuration.LOGGING])
        self.assertIn(Configuration.ENABLE_POINTS_GLUING_LOGGING, config[Configuration.LOGGING])

        # processing configuration
        self.assertIn(Configuration.ASSEMBLY_TARGET_GENOMES, config[Configuration.PROCESSING])
        self.assertIn(Configuration.STRATEGIES, config[Configuration.PROCESSING])
        self.assertIn(Configuration.EXECUTE_SIMPLE_CC_strategy, config[Configuration.PROCESSING][Configuration.STRATEGIES])
        self.assertIn(Configuration.EXECUTE_PHYL_TREE_strategy, config[Configuration.PROCESSING][Configuration.STRATEGIES])
        self.assertIn(Configuration.PHYL_TREE_ASSEMBLY_SCORE_THRESHOLD, config[Configuration.PROCESSING][Configuration.STRATEGIES])

        # output configuration
        self.assertIn(Configuration.OUTPUT_DIRECTORY, config[Configuration.OUTPUT])
        self.assertIn(Configuration.OUTPUT_ASSEMBLIES, config[Configuration.OUTPUT])
        self.assertIn(Configuration.OUTPUT_ASSEMBLIES_AS_CHAINS, config[Configuration.OUTPUT])
        self.assertIn(Configuration.OUTPUT_ASSEMBLIES_DESTINATION_FILES, config[Configuration.OUTPUT])


if __name__ == '__main__':
    unittest.main()
