"""Check the shareable dataset can exercise the production alignment pipeline."""
import json
import unittest
from pathlib import Path

from neuromarketing_heatmaps.processing import load_cleaned, match_gaze_expression

ROOT = Path(__file__).resolve().parents[1]

class PublicDataTest(unittest.TestCase):
    def test_manifest_and_release_rows(self):
        m=json.loads((ROOT/'data'/'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(m['origin_file_count'],12)
        self.assertEqual(len(m['records']),12)
        self.assertGreater(sum(x['rows'] for x in m['records']),200_000)
        self.assertTrue(all((ROOT/x['path']).exists() for x in m['records']))

    def test_real_recording_time_matching(self):
        df=load_cleaned(ROOT/'data'/'public_recordings'/'REC001.csv.gz')
        stimulus=df['SourceStimuliName'].dropna().iloc[0]
        matched=match_gaze_expression(df[df['SourceStimuliName']==stimulus],'Joy',100)
        self.assertGreater(len(matched),100)
        self.assertGreater(matched['Joy'].notna().sum(),100)
        self.assertTrue(matched['delta_ms'].dropna().le(100).all())

if __name__=='__main__':
    unittest.main()
