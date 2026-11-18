import tempfile
import unittest
from pathlib import Path

from src.environment.check import check_environment, EnvironmentCheckError, _read_requirements


class EnvironmentPreflightV088(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / 'requirements.txt').write_text(
            'packaging>=23,<27\npandas>=2.2,<4\nnumpy>=1.26,<3\nscikit-learn==1.9.0\nstreamlit>=1.40,<2\n',
            encoding='utf-8')

    def tearDown(self):
        self.tmp.cleanup()

    def test_core_profile_checks_only_core_dependencies(self):
        result = check_environment(self.root, profile='core', python_version='3.13.5',
                                   installed_versions={'pandas': '2.2.3', 'numpy': '2.3.5'})
        self.assertTrue(result['all_checks_passed'])
        self.assertEqual({x['name'] for x in result['dependency_checks']}, {'pandas', 'numpy'})

    def test_app_profile_detects_missing_streamlit(self):
        result = check_environment(self.root, profile='app', python_version='3.13.5',
                                   installed_versions={'packaging':'25.0','pandas':'2.2.3','numpy':'2.3.5',
                                                       'scikit-learn':'1.9.0','joblib':'1.5.3','plotly':'6.5.2'})
        self.assertFalse(result['all_checks_passed'])
        self.assertIn('streamlit', {x['name'] for x in result['failures']})

    def test_exact_version_mismatch_is_detected(self):
        result = check_environment(self.root, profile='app', python_version='3.13.5',
                                   installed_versions={'packaging':'25.0','pandas':'2.2.3','numpy':'2.3.5',
                                                       'scikit-learn':'1.8.0','joblib':'1.5.3',
                                                       'streamlit':'1.45.0','plotly':'6.5.2'})
        self.assertFalse(result['all_checks_passed'])
        self.assertEqual(result['failures'][0]['name'], 'scikit-learn')

    def test_python_below_minimum_is_rejected(self):
        result = check_environment(self.root, profile='core', python_version='3.9.18',
                                   installed_versions={'pandas':'2.2.3','numpy':'2.3.5'})
        self.assertFalse(result['python']['passed'])
        self.assertFalse(result['all_checks_passed'])

    def test_python_at_exclusive_upper_bound_is_rejected(self):
        result = check_environment(self.root, profile='core', python_version='3.14.0',
                                   installed_versions={'pandas':'2.2.3','numpy':'2.3.5'})
        self.assertFalse(result['all_checks_passed'])

    def test_invalid_profile_rejected(self):
        with self.assertRaises(ValueError):
            check_environment(self.root, profile='unknown')

    def test_missing_requirements_file_fails_closed(self):
        with self.assertRaises(EnvironmentCheckError):
            _read_requirements(self.root / 'missing.txt')

    def test_malformed_requirement_fails_closed(self):
        path = self.root / 'bad.txt'; path.write_text('pandas >>> 2', encoding='utf-8')
        with self.assertRaises(EnvironmentCheckError):
            _read_requirements(path)

    def test_network_and_installation_are_not_invoked(self):
        result = check_environment(self.root, profile='core', python_version='3.13.5',
                                   installed_versions={'pandas':'2.2.3','numpy':'2.3.5'})
        self.assertNotIn('installation_command', result)
        self.assertNotIn('network_request', result)


if __name__ == '__main__':
    unittest.main()
