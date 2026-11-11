import ast,json,tempfile,pathlib,unittest
SOURCE=pathlib.Path(r'C:\Genesis_System3_clean\content\app\app.py')
class CoverageTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory()
  self.addCleanup(self.temp.cleanup)
  self.root=pathlib.Path(self.temp.name)
  self.app_dir=self.root/'content'/'app'
  self.app_dir.mkdir(parents=True)
  self.cache=self.root/'state'/'chain_cache'
  self.cache.mkdir(parents=True)
  tree=ast.parse(SOURCE.read_text(encoding='utf-8'))
  methods=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('_positive_ltp','_chain_cache_coverage')]
  self.assertEqual(len(methods),2)
  ns={'Path':pathlib.Path,'json':json,'APP_DIR':self.app_dir}
  exec(compile(ast.Module(body=methods,type_ignores=[]),str(SOURCE),'exec'),ns)
  self.count=ns['_chain_cache_coverage']
 def write(self,name,data): (self.cache/name).write_text(json.dumps(data),encoding='utf-8')
 def test_empty_is_zero_not_fabricated_80(self):self.assertEqual(self.count(),(0,0))
 def test_valid_and_invalid_prices(self):
  self.write('NIFTY.json',{'contracts':[{'ltp':1},{'ltp':'2.5'},{'ltp':'bad'},{'ltp':None},{'ltp':0.01},None,{'ltp':-4}]})
  self.assertEqual(self.count(),(1,2))
 def test_malformed_json_ignored(self):
  (self.cache/'broken.json').write_text('{not json',encoding='utf-8')
  self.write('good.json',{'contracts':[{'ltp':3}]})
  self.assertEqual(self.count(),(1,1))
 def test_wrong_contract_shape_ignored(self):
  self.write('wrong.json',{'contracts':{'x':1}})
  self.assertEqual(self.count(),(0,0))
 def test_source_both_endpoints_use_shared_helper(self):
  text=SOURCE.read_text(encoding='utf-8')
  self.assertIn('"verified_chain_contracts": _chain_cache_coverage()[1]',text)
  self.assertIn('"verified_chain_contracts_count": verified_contracts',text)
  self.assertNotIn('"verified_chain_contracts": 80',text)
  self.assertNotIn('verified_contracts or 80',text)
if __name__=='__main__':unittest.main(verbosity=2)
