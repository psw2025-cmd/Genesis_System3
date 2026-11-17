import json, unittest
from council import evaluate,parse
class Tests(unittest.TestCase):
    def test_all_pass(self):
        x=evaluate("diff","sha",lambda p,q:'{"verdict":"PASS","findings":[]}')
        self.assertEqual(x["council_verdict"],"PASS")
        self.assertFalse(x["ci_execution_verified"])
    def test_missing_provider(self):
        def caller(p,q):
            if p=="google": raise RuntimeError("offline")
            return '{"verdict":"PASS","findings":[]}'
        self.assertEqual(evaluate("diff","sha",caller)["council_verdict"],"FAIL")
    def test_veto(self):
        self.assertEqual(evaluate("diff","sha",lambda p,q:json.dumps({"verdict":"FAIL" if p=="anthropic" else "PASS","findings":[{"severity":"high","file":"example.py","reason":"unsafe"}] if p=="anthropic" else []}))["council_verdict"],"FAIL")
    def test_bad_schema(self):
        with self.assertRaises(ValueError): parse('{"verdict":"YES","findings":[]}')
    def test_contradiction(self):
        with self.assertRaises(ValueError): parse('{"verdict":"PASS","findings":[{"severity":"high","file":"x","reason":"bug"}]}')
    def test_fail_without_findings(self):
        with self.assertRaises(ValueError): parse('{"verdict":"FAIL","findings":[]}')
    def test_missing_sha(self):
        self.assertEqual(evaluate("diff","",lambda p,q:'{"verdict":"PASS","findings":[]}')["council_verdict"],"FAIL")
if __name__=="__main__":unittest.main()
