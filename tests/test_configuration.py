import os
import unittest

from gos.configuration import Configuration


class ConfigurationTestCase(unittest.TestCase):
    def setUp(self):
        self.init_config = Configuration()

    def test_initialization_top_level(self):
        """ in simple initialization the top level section must be properly configured """
        config = Configuration()
        self.assertIn(config.DIR, config)
        self.assertIn(config.LOGGER, config)
        self.assertIn(config.IOSF, config)
        self.assertIn(config.INPUT, config)
        self.assertIn(config.ALGORITHM, config)
        self.assertIn(config.OUTPUT, config)

        self.assertIsInstance(config[config.LOGGER], dict)
        self.assertIsInstance(config[config.INPUT], dict)
        self.assertIsInstance(config[config.ALGORITHM], dict)
        self.assertIsInstance(config[config.OUTPUT], dict)

    def test_initialization_input_section(self):
        """ input section of the overall configuration must have some default init values and is predefined with them """
        config = Configuration()
        input_section = config[config.INPUT]
        self.assertIn(config.DIR, input_section)
        self.assertIn(config.LOGGER, input_section)
        self.assertIn(config.IOSF, input_section)
        self.assertIn(config.SOURCE, input_section)

        self.assertIsInstance(input_section[config.SOURCE], list)
        self.assertIsInstance(input_section[config.LOGGER], dict)

    def test_initialization_logger_section(self):
        """ logger section is a top level configuration for GOS wide logger """
        config = Configuration()
        logger_section = config[config.LOGGER]
        self.assertIn(config.NAME, logger_section)
        self.assertIn(config.LEVEL, logger_section)
        self.assertIn(config.FORMAT, logger_section)
        self.assertIn(config.DESTINATION, logger_section)

    def test_initialization_output_section(self):
        """ output section configuration for GOS results to be put in"""
        config = Configuration()
        output_section = config[config.OUTPUT]
        self.assertIn(config.DIR, output_section)
        self.assertIn(config.LOGGER, output_section)
        self.assertIn(config.IOSF, output_section)
        self.assertIn(config.ASSEMBLY_POINTS, output_section)
        self.assertIn(config.GENOMES, output_section)
        self.assertIn(config.STATS, output_section)

        self.assertIsInstance(output_section[config.STATS], dict)
        self.assertIsInstance(output_section[config.ASSEMBLY_POINTS], dict)
        self.assertIsInstance(output_section[config.GENOMES], dict)

    def test_initialization_algorithm_section(self):
        """ algorithm section configuration for GOS workflow """
        config = Configuration()
        algorithm_section = config[config.ALGORITHM]
        self.assertIn(config.IOSF, algorithm_section)
        self.assertIn(config.LOGGER, algorithm_section)
        self.assertIn(config.TASKS, algorithm_section)
        self.assertIn(config.STAGES, algorithm_section)
        self.assertIn(config.ROUNDS, algorithm_section)
        self.assertIn(config.PIPELINE, algorithm_section)

        self.assertIsInstance(algorithm_section[config.STAGES], list)
        self.assertIsInstance(algorithm_section[config.ROUNDS], list)
        self.assertIsInstance(algorithm_section[config.TASKS], list)
        self.assertIsInstance(algorithm_section[config.PIPELINE], dict)

    def test_update_with_default_top_level_dir_empty(self):
        """ top level configuration field "dir" default fallback when it is not specified """
        self.init_config[self.init_config.DIR] = None
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.DIR], os.getcwd())
        self.init_config[self.init_config.DIR] = ""
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.DIR], os.getcwd())

    def test_update_with_default_to_level_dir_predefined(self):
        """ top level configuration field "dir" default fallback when it is specified """
        self.init_config[self.init_config.DIR] = os.path.join("dir1", "dir2")
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.DIR], os.path.join("dir1", "dir2"))

    def test_update_with_default_top_level_io_silent_fail_empty(self):
        """ top level configuration field "io_silent_fail" default fallback when its not specified """
        self.init_config[self.init_config.IOSF] = None
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.IOSF], self.init_config.DEFAULT_IOSF)
        self.init_config[self.init_config.IOSF] = ""
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.IOSF], self.init_config.DEFAULT_IOSF)

    def test_update_with_default_top_level_io_silent_fail_predefined(self):
        """ top level configuration field "io_silent_fail" default fallback when its specified """
        self.init_config[self.init_config.IOSF] = True
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.IOSF], True)
        self.init_config[self.init_config.IOSF] = False
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.IOSF], False)
        self.init_config[self.init_config.IOSF] = "CustomValue"  # anything that works for if
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.IOSF], "CustomValue")

    def test_update_with_default_logger_name_empty(self):
        self.init_config[self.init_config.LOGGER][self.init_config.NAME] = ""
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.LOGGER][self.init_config.NAME],
                         self.init_config.DEFAULT_LOGGER_NAME)
        self.init_config[self.init_config.LOGGER][self.init_config.NAME] = None
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.LOGGER][self.init_config.NAME],
                         self.init_config.DEFAULT_LOGGER_NAME)

    def test_update_with_default_logger_name_predefined(self):
        self.init_config[self.init_config.LOGGER][self.init_config.NAME] = True
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.LOGGER][self.init_config.NAME],
                         str(True))
        self.init_config[self.init_config.LOGGER][self.init_config.NAME] = "MyName"
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.LOGGER][self.init_config.NAME],
                         "MyName")

    def test_update_with_default_logger_level_empty(self):
        self.init_config[self.init_config.LOGGER][self.init_config.LEVEL] = ""
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.LOGGER][self.init_config.LEVEL],
                         self.init_config.DEFAULT_LOGGER_LEVEL)
        self.init_config[self.init_config.LOGGER][self.init_config.LEVEL] = None
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.LOGGER][self.init_config.LEVEL],
                         self.init_config.DEFAULT_LOGGER_LEVEL)

    def test_update_with_default_logger_level_predefined(self):
        self.init_config[self.init_config.LOGGER][self.init_config.LEVEL] = "MyLevel"
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.LOGGER][self.init_config.LEVEL],
                         "MyLevel")
        self.init_config[self.init_config.LOGGER][self.init_config.LEVEL] = True
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.LOGGER][self.init_config.LEVEL],
                         str(True))

    def test_update_with_default_logger_format_empty(self):
        self.init_config[self.init_config.LOGGER][self.init_config.FORMAT] = ""
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.LOGGER][self.init_config.FORMAT],
                         self.init_config.DEFAULT_LOGGER_FORMAT)
        self.init_config[self.init_config.LOGGER][self.init_config.FORMAT] = None
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.LOGGER][self.init_config.FORMAT],
                         self.init_config.DEFAULT_LOGGER_FORMAT)

    def test_update_with_default_logger_format_predefined(self):
        self.init_config[self.init_config.LOGGER][self.init_config.FORMAT] = "MyFormat"
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.LOGGER][self.init_config.FORMAT],
                         "MyFormat")
        self.init_config[self.init_config.LOGGER][self.init_config.FORMAT] = True
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.LOGGER][self.init_config.FORMAT],
                         str(True))

if __name__ == '__main__':
    unittest.main()
