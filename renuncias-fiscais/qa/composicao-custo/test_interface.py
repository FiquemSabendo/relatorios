from playwright.sync_api import sync_playwright
import json
from pathlib import Path
out=Path('renuncias-fiscais/qa/composicao-custo')
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/home/laltuf/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome',headless=True)
 page=b.new_page(viewport={'width':1300,'height':1000});errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8765/docs/renuncias-fiscais/index.html#composicao')
 page.locator('#comp-arvore details').first.wait_for()
 assert page.locator('[data-v="renuncia-lucro"]').count()==0
 for tab in ['apresentacao','metodologia','inconsistencias','beneficiarios','setores','composicao','custo-fiscal']:
  page.locator(f'[data-v="{tab}"]').click()
  assert page.locator('#view-'+tab).is_visible()
 assert page.locator('#custo-table tbody tr').count()==6
 assert '166,31' in page.locator('#custo-table').inner_text()
 for tab in ['composicao','custo-fiscal']:
  page.locator(f'[data-v="{tab}"]').click()
  for width in [1300,420]:
   page.set_viewport_size({'width':width,'height':1000})
   assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),(tab,width)
   page.screenshot(path=str(out/f'{tab}-{width}.png'),full_page=True)
 page.locator('[data-v="composicao"]').click()
 page.select_option('#comp-ano','2023')
 page.select_option('#comp-tipo',index=1)
 assert page.locator('#comp-arvore > details').count()==1
 page.locator('#comp-busca').fill('zzzzzzsemresultado');page.wait_for_timeout(300)
 assert page.locator('#comp-fundamentos tbody tr').count()==0
 page.locator('#comp-busca').fill('');page.wait_for_timeout(300)
 assert page.locator('#comp-fundamentos tbody tr').count()>0
 assert not errors,errors
 print('PASS: 7 abas; filtros; tabela de 6 comparadores; nenhum erro JS; sem overflow em 1300/420px.')
 b.close()
