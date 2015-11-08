import unittest

from gos.configuration import Configuration


class ConfigurationTestCase(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
