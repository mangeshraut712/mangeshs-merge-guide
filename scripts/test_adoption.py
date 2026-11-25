import datetime
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

SPEC = importlib.util.spec_from_file_location('adoption', Path(__file__).with_name('update-adoption.py'))
adoption = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adoption)


class AdoptionTests(unittest.TestCase):
    def test_only_404_means_missing(self):
        with patch.object(adoption.urllib.request, 'urlopen', side_effect=urllib.error.HTTPError('https://example.com', 404, 'missing', {}, None)):
            self.assertIsNone(adoption.fetch('https://example.com'))
        for code in (401, 403, 429, 500):
            with self.subTest(code=code), patch.object(adoption.urllib.request, 'urlopen', side_effect=urllib.error.HTTPError('https://example.com', code, 'error', {}, None)):
                with self.assertRaises(urllib.error.HTTPError):
                    adoption.fetch('https://example.com')

    def test_missing_package_keeps_downloads_unknown_and_paginates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'scripts').mkdir()
            (root / 'docs').mkdir()
            (root / 'package.json').write_text(json.dumps({'name': '@owner/pkg', 'repository': {'url': 'git+https://github.com/owner/repo.git'}}))
            responses = [{'stargazers_count': 2, 'forks_count': 3}, [{'assets': [{'download_count': 4}]}] * 100, [{'assets': [{'download_count': 1}]}]]
            with patch.object(adoption, '__file__', str(root / 'scripts/update-adoption.py')), patch.object(adoption, 'github', side_effect=responses), patch.object(adoption, 'fetch', return_value=None) as fetch, patch('sys.stdout', new=io.StringIO()):
                adoption.main()
            snapshot = json.loads((root / 'docs/adoption.json').read_text())
            self.assertEqual(snapshot['github']['release_asset_downloads_lifetime'], 401)
            self.assertEqual(snapshot['npm']['status'], 'not_published')
            self.assertIsNone(snapshot['npm']['last_month'])
            self.assertEqual(fetch.call_count, 1)

    def test_network_error_does_not_replace_previous_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'scripts').mkdir()
            (root / 'docs').mkdir()
            (root / 'package.json').write_text(json.dumps({'name': '@owner/pkg', 'repository': {'url': 'https://github.com/owner/repo.git'}}))
            target = root / 'docs/adoption.json'
            target.write_text('previous snapshot')
            with patch.object(adoption, '__file__', str(root / 'scripts/update-adoption.py')), patch.object(adoption, 'github', side_effect=TimeoutError('network')):
                with self.assertRaises(TimeoutError):
                    adoption.main()
            self.assertEqual(target.read_text(), 'previous snapshot')


    def test_published_package_records_downloads_and_parses_repository_url(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'scripts').mkdir()
            (root / 'docs').mkdir()
            (root / 'package.json').write_text(json.dumps({'name': '@owner/pkg', 'repository': {'url': 'git+https://github.com/owner/repo.git'}}))
            downloads = {'downloads': 42, 'package': '@owner/pkg'}
            target = root / 'docs/adoption.json'
            target.write_text('previous snapshot')
            with patch.object(adoption, '__file__', str(root / 'scripts/update-adoption.py')), \
                    patch.object(adoption, 'github', side_effect=[{'stargazers_count': 2, 'forks_count': 3}, []]) as github, \
                    patch.object(adoption, 'fetch', side_effect=[{'name': '@owner/pkg'}, downloads]) as fetch, \
                    patch('sys.stdout', new=io.StringIO()):
                adoption.main()
            snapshot = json.loads(target.read_text())
            self.assertEqual(snapshot['repository'], 'owner/repo')
            self.assertEqual([call.args[0] for call in github.call_args_list], ['repos/owner/repo', 'repos/owner/repo/releases?per_page=100&page=1'])
            self.assertEqual([call.args[0] for call in fetch.call_args_list], [
                'https://registry.npmjs.org/%40owner%2Fpkg',
                'https://api.npmjs.org/downloads/point/last-month/%40owner%2Fpkg',
            ])
            self.assertEqual(snapshot['npm']['status'], 'published')
            self.assertEqual(snapshot['npm']['last_month'], downloads)
            self.assertEqual(snapshot['github']['release_asset_downloads_lifetime'], 0)
            checked = datetime.datetime.fromisoformat(snapshot['checked_at'])
            self.assertEqual(checked.utcoffset(), datetime.timedelta(0))
            self.assertFalse((root / 'docs/adoption.json.tmp').exists())

if __name__ == '__main__':
    unittest.main()
