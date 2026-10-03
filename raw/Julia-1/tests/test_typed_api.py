import unittest
from unittest.mock import Mock
from julia.router.engine import FastEngine

class TypedAPITests(unittest.TestCase):
    def setUp(self):
        self.engine=FastEngine.__new__(FastEngine)
        self.engine.logits=Mock(return_value=[[0.,2.],[0.,0.,0.],[0.,0.]])
    def test_named_questions_keep_ids_and_full_probabilities(self):
        questions={'team':dict(type='choice',instructions='route',criteria={'billing':'Payments','access':'Login'}),
                   'severity':dict(type='score',instructions='rate',criteria=['low','medium','high']),
                   'approved':dict(type='noul',instructions='approve?')}
        result=self.engine.predict(state='context',questions=questions)['answers']
        self.assertEqual(result['team']['choice'],'access')
        self.assertAlmostEqual(result['severity']['score'],1.)
        self.assertEqual(result['approved']['noul'],.5)
        self.assertAlmostEqual(sum(result['team']['probabilities'].values()),1.)
        self.assertEqual(self.engine.logits.call_args.args[0][0]['options'],['Payments','Login'])
    def test_invalid_questions_rejected_before_inference(self):
        for questions in ({},{'q':dict(type='choice',instructions='q',criteria={'a':'a'})},
                          {'q':dict(type='choice',instructions='q',criteria={str(i):str(i) for i in range(21)})}):
            with self.assertRaises(ValueError):self.engine.predict(state='s',questions=questions)
        self.engine.logits.assert_not_called()
    def test_positional_state_matches_keyword_state(self):
        self.engine.logits.return_value=[[1.,0.]]
        q={'q':dict(type='choice',instructions='q',criteria={'a':'A','b':'B'})}
        self.assertEqual(self.engine.predict('s',q),self.engine.predict(state='s',questions=q))

    def test_noul_preserves_descriptions_in_false_true_order(self):
        self.engine.logits.return_value=[[0.,2.]]
        questions={'review':dict(type='noul',instructions='Needs human review?',
            criteria={'true':'A human should inspect this run.',
                      'false':'No human attention is warranted.'})}
        answer=self.engine.predict(state='context',questions=questions)['answers']['review']
        self.assertEqual(self.engine.logits.call_args.args[0][0]['options'],
                         ['No human attention is warranted.','A human should inspect this run.'])
        self.assertEqual(list(answer['probabilities']),['false','true'])
        self.assertGreater(answer['noul'],.5)

    def test_noul_rejects_invalid_criteria_before_inference(self):
        self.engine.logits.return_value=[[0.,2.]]
        for criteria in ({}, {'true':'yes'}, {'false':'no','true':'yes','other':'maybe'},
                         ['no','yes'], {'false':'','true':'yes'}):
            with self.subTest(criteria=criteria):
                questions={'q':dict(type='noul',instructions='q',criteria=criteria)}
                with self.assertRaises(ValueError):
                    self.engine.predict(state='context',questions=questions)
        self.engine.logits.assert_not_called()
