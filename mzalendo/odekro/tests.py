import os
import datetime
# import time
# import json
# import tempfile
# import subprocess

# from unittest import TestCase

import unittest

from management.hansard_parser import parse, parse_time
from utils import split_name, legal_name


class ImporterTest(unittest.TestCase):
    NAMES =  (
        ('Abayateye, Alfred W. G.', 
            ('Abayateye', 'Alfred', 'W. G.', ''),
            'Alfred W. G. Abayateye'),
        ('Abongo, Albert', ('Abongo', 'Albert', '', ''),
            'Albert Abongo'),
        ('Abdul-Karim, Iddrisu (Alhaji)', 
            ('Abdul-Karim', 'Iddrisu', '', 'Alhaji'),
            'Iddrisu Abdul-Karim'),
        ('Abdul-Rahman, Masoud Baba', 
            ('Abdul-Rahman', 'Masoud', 'Baba', ''),
            'Masoud Baba Abdul-Rahman'),
        ('Abubakari, Ibrahim Dey (Alhaji)', 
            ('Abubakari', 'Ibrahim', 'Dey', 'Alhaji'),
            'Ibrahim Dey Abubakari'),
        ('Ameyaw-Akumfi, Christopher (Prof)', 
            ('Ameyaw-Akumfi', 'Christopher', '', 'Prof'),
            'Christopher Ameyaw-Akumfi'),
        ('Alhassan, Ahmed Yakubu (Dr)', 
            ('Alhassan', 'Ahmed', 'Yakubu', 'Dr'),
            'Ahmed Yakubu Alhassan'),
        ('Ahmed, Mustapha (Maj [rtd]) (Dr) (Alh)', 
            ('Ahmed', 'Mustapha', '', 'Maj (rtd) Dr Alh'),
            'Mustapha Ahmed')
    )

    def test_split_name(self):
        for name, split, legal in self.NAMES:
            self.assertEqual(split, split_name(name))
            last_name, first_name, middle_name, title = split
            self.assertEqual(legal, 
                    legal_name(last_name, first_name, middle_name))


class GhanaParserTest(unittest.TestCase):
    basedir = os.path.abspath(os.path.dirname( __file__ ))
    sample = os.path.join(basedir, 'data', 'hansard-sample.txt')
    
    entries = None
    head = None


    @classmethod
    def setUpClass(cls):
        cls.head, cls.entries = parse(open(cls.sample, 'r').readlines())

    @classmethod
    def tearDownClass(cls):
        pass

    def test_parse_time_string(self):
        
        data = {
            '1.00 p.m.':  datetime.time(13),
            '1.00 a.m.':  datetime.time(1),
            '12.00 p.m.': datetime.time(12), # am and pm make no sense at noon or midnight - but define what we want to happen
            '12.30 p.m.': datetime.time(12, 30)
        }
        
        for s, t in data.items():
            self.assertEqual(parse_time(s), t)

        self.assertIsNone(parse_time('foo.bar'))
        

    def test_header(self):
        self.assertEqual(4, self.head['series'])
        self.assertEqual(76, self.head['volume'])
        self.assertEqual(13, self.head['number'])
        self.assertEqual(datetime.date(2012, 2, 14), self.head['date'])
        self.assertEqual(datetime.time(10, 40), self.head['time'])

    def test_entries(self):
        t = datetime.time(10, 40)

        x = self.entries[0]
        self.assertTrue(x['text'].lower().endswith('speaker in the chair'))
        self.assertEqual(t, x['time'])

        x = self.entries[1]
        self.assertEqual('PRAYERS', x['text'])
        self.assertEqual(t, x['time'])

        topic = 'Votes and Proceedings and the Official Report'
        

        speeches = [x for x in self.entries if x['kind'] is 'speech']

        self.assertEqual(122, len(speeches))
        
        x = self.entries[0]

        self.assertEqual(topic, x['topic'])
        self.assertEqual('Madam Speaker', x['name'])


        x = self.entries[-1]
        self.assertEqual('ADJOURNMENT', x['text'])
        self.assertEqual(datetime.time(13, 20), x['time'])
        self.assertEqual(datetime.datetime(2012, 2, 15, 10), x['next'])

    def test_page_order(self):
        pass


if __name__ == "__main__":
    unittest.main()