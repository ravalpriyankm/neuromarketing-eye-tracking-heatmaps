"""Local tests for offline, reproducible research processing."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

from neuromarketing_heatmaps.demo import build_demo
from neuromarketing_heatmaps.processing import (
    DataError, clean_export, find_header_line, gaze_points,
    match_gaze_expression, read_export, load_cleaned,
    dataset_summary, workbook_from_cleaned,
)
from neuromarketing_heatmaps.visualisation import density_map, render_heatmap

ROOT = Path(__file__).resolve().parents[1]


class ProcessingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.folder = Path(cls.tmp.name)
        cls.raw, cls.image = build_demo(cls.folder)
        cls.cleaned = read_export(cls.raw, participant='TEST001')

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_read_header_and_cleaned(self):
        self.assertEqual(find_header_line(self.raw), 2)
        self.assertGreater(len(self.cleaned), 320)
        self.assertEqual(self.cleaned.Participant.unique().tolist(), ['TEST001'])
        self.assertFalse(self.cleaned.SlideEvent.eq('EndMedia').any())

    def test_data_preserves_missing_scores(self):
        self.assertTrue(self.cleaned.Joy.isna().any())
        self.assertTrue(self.cleaned.ET_GazeLeftx.isna().any())
        self.assertGreater(self.cleaned.Joy.notna().sum(), 0)

    def test_missing_schema_rejected(self):
        with self.assertRaises(DataError):
            clean_export(pd.DataFrame({'Timestamp':[1]}), participant='N')

    def test_gaze_one_eye_valid(self):
        df=pd.DataFrame({'Timestamp':[10,20,30], 'Participant':['A']*3,
          'SourceStimuliName':['S']*3, 'ET_GazeLeftx':[10, np.nan, np.nan],
          'ET_GazeLefty':[20,np.nan,np.nan], 'ET_GazeRightx':[30,50,np.nan],
          'ET_GazeRighty':[40,60,np.nan]})
        out=gaze_points(df)
        self.assertEqual(len(out),2)
        self.assertEqual(list(out.gaze_x),[20,50])
        self.assertEqual(list(out.gaze_y),[30,60])

    def test_temporal_matching_uses_same_stimulus_and_recording(self):
        rows=[]
        def row(t,p,s,x,y,joy):
            rows.append({'Timestamp':t,'Participant':p,'SourceStimuliName':s,
              'ET_GazeLeftx':x,'ET_GazeLefty':y,'ET_GazeRightx':x,'ET_GazeRighty':y,'Joy':joy})
        row(100, 'A','S',50,50, np.nan)
        row(105, 'A','S',np.nan,np.nan,80)
        row(103, 'B','S',np.nan,np.nan,99)
        row(104, 'A','T',np.nan,np.nan,77)
        matched=match_gaze_expression(pd.DataFrame(rows),'Joy',10)
        self.assertEqual(len(matched),1)
        self.assertEqual(matched.Joy.iloc[0],80)
        self.assertEqual(matched.delta_ms.iloc[0],5)

    def test_time_matching_excludes_outside_tolerance(self):
        df=self.cleaned.copy()
        out=match_gaze_expression(df,'Joy',0.01)
        self.assertTrue(out.Joy.isna().any())
        self.assertRaises(DataError, match_gaze_expression, df,'Joy',-5)

    def test_heatmap_generated_offline(self):
        out=self.folder / 'gaze_test.png'
        stats=render_heatmap(self.cleaned,self.image,out,
            stimulus='synthetic_stimulus', display_width=1280,display_height=720,bins=50)
        self.assertGreater(stats['temporally_matched_and_in_bounds_samples'],100)
        self.assertTrue(out.is_file())
        with Image.open(out) as im:
            self.assertGreater(im.width,300)

    def test_weighted_heatmap_generated_offline(self):
        out=self.folder / 'joy_test.png'
        stats=render_heatmap(self.cleaned,self.image,out,
            stimulus='synthetic_stimulus', display_width=1280,display_height=720,
            expression='Joy', tolerance_ms=100, bins=50)
        self.assertGreater(stats['temporally_matched_and_in_bounds_samples'],10)
        self.assertTrue(out.is_file())

    def test_bad_calibration_and_signed_valence_rejected(self):
        with self.assertRaises(DataError):
            render_heatmap(self.cleaned,self.image,self.folder/'no.png',stimulus='synthetic_stimulus', display_width=0,display_height=720)
        with self.assertRaises(DataError):
            render_heatmap(self.cleaned,self.image,self.folder/'no2.png',stimulus='synthetic_stimulus', display_width=1280,display_height=720,expression='Valence')

    def test_density_map_shape_and_finite_values(self):
        arr=density_map(np.array([.1,.2,.4]),np.array([.2,.5,.7]),bins=32)
        self.assertEqual(arr.shape,(32,32))
        self.assertTrue(np.isfinite(arr).all())
        self.assertAlmostEqual(float(arr.max()),1.0)

    def test_workbook_generation(self):
        destination=self.folder/'survey.xlsx'
        workbook_from_cleaned(self.cleaned,destination)
        self.assertTrue(destination.is_file())
        self.assertGreater(destination.stat().st_size,1000)

    def test_csv_gzip_roundtrip(self):
        destination=self.folder/'cleaned.csv.gz'
        self.cleaned.to_csv(destination,index=False,compression='gzip')
        self.assertEqual(len(load_cleaned(destination)),len(self.cleaned))

    def test_dataset_summary(self):
        result=dataset_summary(self.cleaned)
        self.assertEqual(result['participants'],1)
        self.assertGreater(result['gaze_samples'],300)

    def test_cli_stimulus_listing(self):
        dest=self.folder/'sample.csv'
        self.cleaned.to_csv(dest,index=False)
        result=subprocess.run([sys.executable,'-m','neuromarketing_heatmaps','stimuli',str(dest)],cwd=ROOT, capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)['stimuli'][0]['name'],'synthetic_stimulus')

    def test_no_original_raw_participants_in_public_package(self):
        self.assertFalse((ROOT/'raw_data.zip').exists())
        self.assertFalse((ROOT/'data'/'original').exists())
        self.assertFalse((ROOT/'experiment_images.zip').exists())
        self.assertTrue((ROOT/'data'/'manifest.json').is_file())

    def test_public_recordings_deidentified_fields(self):
        paths=sorted((ROOT/'data'/'public_recordings').glob('*.csv.gz'))
        self.assertEqual(len(paths),12)
        names=set()
        for path in paths:
            frame=pd.read_csv(path,nrows=4)
            names.update(frame['Participant'].astype(str))
            self.assertTrue({'Timestamp','SourceStimuliName','ET_GazeLeftx','Joy'}.issubset(frame.columns))
            self.assertFalse({'Age','Gender','RecordingDate','RespondentName','Respondent ID'} & set(frame.columns))
        self.assertEqual(names,{f'REC{i:03d}' for i in range(1,13)})

    def test_legacy_notebooks_have_no_cached_outputs(self):
        for path in (ROOT/'legacy').glob('*.ipynb'):
            content=json.loads(path.read_text(encoding='utf-8'))
            for cell in content['cells']:
                if cell['cell_type']=='code':
                    self.assertEqual(cell.get('outputs',[]),[])
                    self.assertNotIn('C:\\Users\\', ''.join(cell['source']))

if __name__=='__main__':
    unittest.main()
