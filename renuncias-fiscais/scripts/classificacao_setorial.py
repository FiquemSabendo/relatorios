"""Classificação editorial de atividade; regras específicas precedem divisões CNAE.
Não modifica CNAE, valores ou agrupamento por raiz. Fonte e regras exportadas para QA.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
VERSION='2026-09-17.2'
SETOR_POR_ATIVIDADE=json.loads((ROOT/'data/classificacao-setorial/setores.json').read_text())
# Classes ou grupos que precisam de recorte mais informativo que a divisão.
ESPECIFICAS={
 '011': 'Agricultura', '012':'Agricultura', '013':'Agricultura', '014':'Sementes e mudas', '015':'Pecuária', '016':'Serviços agropecuários',
 '071':'Mineração de ferro','072':'Mineração de outros metais','081':'Mineração de pedra, areia e argila',
 '091':'Petróleo e gás','099':'Serviços de mineração',
 '101':'Carnes e frigoríficos','102':'Pescados','103':'Frutas e vegetais processados','104':'Óleos e gorduras vegetais','105':'Laticínios','106':'Moagem e alimentos farináceos','107':'Açúcar','108':'Café','109':'Outros alimentos',
 '111':'Bebidas alcoólicas','112':'Bebidas não alcoólicas','193':'Biocombustíveis',
 '20134':'Fertilizantes','20126':'Fertilizantes','20142':'Gases industriais','20517':'Defensivos agrícolas','206':'Limpeza e cosméticos','207':'Tintas e vernizes',
 '221':'Borracha e pneus','222':'Plásticos','231':'Vidro','232':'Cimento','233':'Artefatos de concreto','234':'Cerâmica','239':'Outros minerais não metálicos',
 '241':'Siderurgia','242':'Siderurgia','243':'Siderurgia','244':'Metalurgia de metais não ferrosos','245':'Fundição',
 '261':'Componentes eletrônicos','262':'Informática','263':'Equipamentos de comunicação','264':'Áudio e vídeo','265':'Instrumentos de medição','266':'Equipamentos médicos','267':'Óptica e fotografia',
 '275':'Eletrodomésticos','283':'Máquinas agrícolas','28518':'Equipamentos para petróleo e gás','285':'Máquinas para construção e mineração',
 '291':'Automóveis','292':'Caminhões e ônibus','293':'Carrocerias e reboques','294':'Autopeças','295':'Recondicionamento de motores',
 '301':'Construção naval','303':'Material ferroviário','304':'Indústria aeronáutica','30911':'Motocicletas','30920':'Bicicletas',
 '33163':'Manutenção aeronáutica','33171':'Manutenção naval',
 '462':'Comércio de matérias-primas agropecuárias','46354':'Comércio de bebidas','46362':'Tabaco','463':'Comércio de alimentos',
 '46419':'Têxteis e vestuário','46427':'Têxteis e vestuário','46435':'Calçados e artigos de couro','46443':'Farmacêutico','46451':'Equipamentos médicos','46460':'Limpeza e cosméticos','46478':'Livros e papelaria',
 '46516':'Informática','46524':'Equipamentos de comunicação','46613':'Máquinas agrícolas','46621':'Máquinas para construção e mineração','46648':'Equipamentos médicos','466':'Comércio de máquinas e equipamentos','467':'Materiais de construção',
 '46818':'Combustíveis','46826':'Combustíveis','46834':'Insumos agropecuários','46842':'Químico','46851':'Siderurgia e metalurgia','46869':'Papel e embalagens','46877':'Reciclagem e sucata',
 '46915':'Comércio de alimentos','46923':'Insumos agropecuários',
 '47113':'Supermercados','47121':'Supermercados','47237':'Comércio de bebidas','47296':'Comércio de alimentos e tabaco','472':'Comércio de alimentos','473':'Combustíveis','474':'Materiais de construção',
 '47512':'Informática','47521':'Equipamentos de comunicação','47539':'Eletrodomésticos','47547':'Móveis e decoração','47555':'Têxteis e vestuário','47610':'Livros e papelaria','47717':'Farmacêutico','47725':'Limpeza e cosméticos','47733':'Equipamentos médicos','47741':'Óptica','47814':'Têxteis e vestuário','47822':'Calçados e artigos de couro','47849':'Combustíveis',
 '491':'Transporte ferroviário','492':'Transporte rodoviário de passageiros','493':'Transporte rodoviário de cargas','494':'Transporte dutoviário','495':'Outros transportes terrestres',
 '503':'Navegação de apoio','511':'Aérea','512':'Aérea','513':'Transporte espacial','52401':'Serviços aeroportuários',
 '551':'Hotéis e hospedagem','559':'Outros alojamentos','561':'Restaurantes e alimentação','562':'Alimentação coletiva e bufês',
 '601':'Rádio','602':'Televisão','631':'Internet e processamento de dados','639':'Serviços de informação',
 '642':'Bancos','643':'Crédito e financiamento','644':'Arrendamento mercantil financeiro','645':'Capitalização','646':'Holdings e participações','647':'Fundos de investimento','649':'Outros serviços financeiros',
 '711':'Engenharia e arquitetura','712':'Testes e análises técnicas','771':'Locação de veículos','772':'Locação de objetos pessoais','773':'Locação de máquinas e equipamentos','774':'Gestão de ativos intangíveis',
 '851':'Educação básica','852':'Educação básica','853':'Ensino superior','854':'Educação profissional','855':'Apoio à educação','859':'Outras atividades de ensino',
 '861':'Hospitais','862':'Atendimento móvel de saúde','863':'Consultórios e clínicas','864':'Diagnóstico e terapias','865':'Profissionais de saúde','866':'Gestão de saúde','869':'Outros serviços de saúde',
}
DIVISOES={
 '01':'Agropecuária','02':'Silvicultura','03':'Pesca e aquicultura','05':'Carvão mineral','06':'Petróleo e gás','07':'Mineração de metais','08':'Mineração não metálica','09':'Serviços de extração mineral',
 '10':'Alimentos','11':'Bebidas','12':'Tabaco','13':'Têxtil','14':'Vestuário','15':'Calçados e artigos de couro','16':'Madeira','17':'Papel e celulose','18':'Impressão e reprodução','19':'Refino e derivados de petróleo','20':'Químico','21':'Farmacêutico','22':'Borracha e plástico','23':'Minerais não metálicos','24':'Metalurgia','25':'Produtos de metal','26':'Eletrônicos e informática','27':'Equipamentos elétricos','28':'Máquinas e equipamentos','29':'Automotivo','30':'Outros equipamentos de transporte','31':'Móveis','32':'Outras indústrias','33':'Manutenção e instalação industrial',
 '35':'Energia elétrica e gás','36':'Abastecimento de água','37':'Esgoto','38':'Resíduos e reciclagem','39':'Descontaminação ambiental','41':'Construção Civil','42':'Construção Civil','43':'Construção Civil','45':'Comércio e reparação de veículos','46':'Comércio atacadista — diversos','47':'Comércio varejista — diversos','49':'Transporte terrestre','50':'Transporte aquaviário','51':'Aérea','52':'Armazenagem e serviços de transporte','53':'Correios e entregas','55':'Hospedagem','56':'Alimentação','58':'Edição de livros e periódicos','59':'Audiovisual e música','60':'Rádio e televisão','61':'Telecomunicações','62':'Tecnologia da informação','63':'Serviços de informação','64':'Serviços financeiros','65':'Seguros e previdência','66':'Serviços auxiliares financeiros','68':'Imobiliário','69':'Serviços jurídicos e contábeis','70':'Consultoria e sedes de empresas','71':'Engenharia e serviços técnicos','72':'Pesquisa e desenvolvimento','73':'Publicidade e pesquisa de mercado','74':'Outros serviços profissionais','75':'Veterinária','77':'Locação de bens','78':'Seleção e locação de mão de obra','79':'Turismo e agências de viagens','80':'Segurança e vigilância','81':'Limpeza e serviços prediais','82':'Serviços administrativos','84':'Administração pública','85':'Educação','86':'Saúde','87':'Cuidados e assistência com alojamento','88':'Assistência social','90':'Artes e espetáculos','91':'Cultura e patrimônio','92':'Jogos e apostas','93':'Esporte e recreação','94':'Associações e organizações','95':'Reparação de bens pessoais e informática','96':'Serviços pessoais','97':'Serviços domésticos','99':'Organismos internacionais',
}
def classificar_cnae(code):
    code=str(code or '').zfill(5)
    if code=='00000' or len(code)!=5 or not code.isdigit():return ('Não identificado','sem_cnae')
    for size in (5,3):
        if code[:size] in ESPECIFICAS:return (ESPECIFICAS[code[:size]],f'cnae_{size}:{code[:size]}')
    if code[:2] in DIVISOES:return (DIVISOES[code[:2]],f'cnae_2:{code[:2]}')
    return ('Não identificado','cnae_nao_mapeada')

def classificar_estabelecimentos(estabs):
    """Tuplas estab_id, CNPJ, razão, fantasia, CNAE, município, UF.
    Inferência de raiz apenas para CNAE ausente, se todas as atividades conhecidas
    da raiz receberem o mesmo rótulo. Não inventa um CNAE para o estabelecimento.
    """
    root_known={}
    for eid,cnpj,razao,fant,cnae,mun,uf in estabs:
        label,rule=classificar_cnae(cnae)
        if label!='Não identificado' and len(cnpj)==14 and cnpj.isdigit():
            root_known.setdefault(cnpj[:8],{}).setdefault(label,set()).add(cnae)
    overrides=json.loads((ROOT/'data/classificacao-setorial/curadoria.json').read_text())
    rows=[]
    for eid,cnpj,razao,fant,cnae,mun,uf in estabs:
        label,rule=classificar_cnae(cnae);source='CNAE declarada no Portal da Transparência';base=cnae
        root=cnpj[:8] if len(cnpj)==14 and cnpj.isdigit() else ''
        if label=='Não identificado':
            if root in overrides:
                o=overrides[root];label=o['setor'];rule='curadoria_raiz:'+root;source=o['fonte'];base=o['evidencia']
            elif len(root_known.get(root,{}))==1:
                label=next(iter(root_known[root]));rule='inferencia_mesma_raiz';source='CNAEs informadas em outros estabelecimentos da mesma raiz no snapshot';base=', '.join(sorted(root_known[root][label]))
        rows.append(dict(estab_id=eid,cnpj=cnpj,razao_social=razao,cnae_original=cnae,setor=SETOR_POR_ATIVIDADE[label],atividade=label,regra=rule,fonte=source,evidencia=base))
    return rows
