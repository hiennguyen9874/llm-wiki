import unittest
import numpy as np

from decisions_api import assemble, build_plan
from prompt_templates import build_prompt_plan, finish_answers


class PromptChecks(unittest.TestCase):
    def test_default_is_identical_and_explicit_rubrics_preserved(self):
        body = {"model":"m", "state":"Facts.", "questions":{
            "b":{"type":"noul","instructions":"Claim.","criteria":{"true":"Supported.","false":"Refuted."}},
            "c":{"type":"choice","instructions":"Pick.","criteria":{"a":"Alpha.","b":"Beta."}}}}
        old = build_plan(body)
        p = build_prompt_plan(body)
        self.assertEqual(old.pairs, p.pairs)
        e = np.array([.2,.8,.7,.1])
        self.assertEqual(assemble(old,e), finish_answers(p,e))
        direct = build_prompt_plan(body,"direct_noul")
        self.assertEqual(old.pairs,direct.pairs)
        plain = build_prompt_plan(body,"unquoted")
        self.assertIn("Alpha.",plain.pairs[2][1])

    def test_direct_boolean_and_following_option_offsets(self):
        body = {"model":"m", "state":"Facts.", "questions":{
            "b":{"type":"noul","instructions":"Claim."},
            "c":{"type":"choice","instructions":"Pick.","criteria":{"a":"Alpha.","b":"Beta."}}}}
        p = build_prompt_plan(body,"direct_noul")
        self.assertEqual(len(p.pairs),3)
        self.assertEqual(p.pairs[0][1],"Claim.")
        out=finish_answers(p,[.1,.2,.8])
        self.assertEqual(out["b"]["noul"],.1)
        self.assertEqual(out["c"]["choice"],"b")

    def test_multiwindow_assertion_uses_any_support(self):
        body={"model":"m","state":"x"*25000,"questions":{"b":{"type":"noul","instructions":"Claim."}}}
        p=build_prompt_plan(body,"direct_noul")
        self.assertEqual(finish_answers(p,[.1,.9])["b"]["noul"],.9)


if __name__ == "__main__":
    unittest.main()
