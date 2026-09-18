from pathlib import Path
import json
from playwright.sync_api import sync_playwright
Q=Path(__file__).resolve().parent
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/home/laltuf/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome',headless=True)
 page=b.new_page(viewport={'width':1400,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8765/docs/renuncias-fiscais/index.html#beneficiarios')
 page.locator('#res-corpo tr').first.wait_for()
 assert page.locator('h1').inner_text()=='Benefícios tributários por beneficiário'
 assert 'beneficiários agrupados por raiz do CNPJ' in page.locator('#busca-hits').inner_text()
 # Validar todos os anos, inclusive cobertura parcial de 2024.
 annual=page.evaluate('''()=>AP.anos.map((r,a)=>({ano:r.ano,calculado:conv(r.nominal,a,'real'),esperado:r.real,diferenca:conv(r.nominal,a,'real')-r.real}))''')
 assert all(abs(r['diferenca'])<.001 for r in annual)
 page.locator('#res-corpo tr').first.click()
 nominal=page.locator('.kv .v').first.inner_text()
 page.locator('#det-medida [data-medida="real"]').click()
 assert 'agosto de 2026' in page.locator('#det-medida').inner_text()
 details=page.evaluate('''()=>{const F=fatia(true),g=S.aberta;const total=Array.from({length:NA},(_,a)=>conv(F.vals[g*NA+a],a,'real')).reduce((s,v)=>s+v,0);return {nome:F.E.nome[g],total,referencia:AP.beneficiarios.valor_petrobras,diferenca:total-AP.beneficiarios.valor_petrobras,formatado:formatadoresDetalhe().fmtV(total)}}''')
 assert abs(details['diferenca'])<100
 assert page.locator('.kv .v').first.inner_text()==details['formatado']
 page.locator('.detbox').screenshot(path=str(Q/'detalhe-real.png'))
 page.locator('#det-medida [data-medida="nominal"]').click()
 assert page.locator('.kv .v').first.inner_text()==nominal
 for tab in ['apresentacao','metodologia','setores','composicao']:
  page.locator(f'[data-v="{tab}"]').click()
  assert page.locator('#view-'+tab).is_visible()
 assert 'janeiro a dezembro de 2023' not in page.locator('#view-metodologia').inner_text()
 assert not errors,errors
 result=dict(anos=annual,petrobras=details,nominal=nominal,erros_js=errors,base='agosto de 2026')
 (Q/'validacao.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 print(json.dumps(result,ensure_ascii=False,indent=2));b.close()
