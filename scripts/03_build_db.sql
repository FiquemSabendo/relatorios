-- ============================================================================
-- renuncias.duckdb — Renúncias fiscais federais por beneficiário, 2015-2024
-- Fonte: Portal da Transparência / CGU (dados da Receita Federal)
-- Rodar da raiz do projeto:  duckdb renuncias.duckdb < scripts/03_build_db.sql
-- ============================================================================

-- ---------------------------------------------------------------- staging --
-- all_varchar é obrigatório: o valor vem como "401617,00" (vírgula decimal)
-- e o CNPJ tem zeros à esquerda que um cast automático destruiria.

CREATE OR REPLACE TABLE stg_beneficiario AS
SELECT
    CAST("Ano-calendário" AS INTEGER)                             AS ano,
    CNPJ                                                          AS cnpj,
    trim("Razão Social")                                          AS razao_social,
    trim("Nome Fantasia")                                         AS nome_fantasia,
    -- a base traz um registro-sentinela ("Inválido", CNPJ -3) com CNAE nulo;
    -- normalizar aqui mantém esse valor dentro dos totais, em "Sem informação"
    coalesce("Código CNAE", '00000')                              AS cnae,
    coalesce(nullif(trim(CNAE), ''), 'Sem informação')            AS cnae_desc,
    trim("Município")                                             AS municipio,
    trim(UF)                                                      AS uf,
    CAST(replace("Valor Renúncia Fiscal (R$)", ',', '.') AS DOUBLE) AS valor
FROM read_csv('data/raw/*/*_RenúnciasFiscaisPorBeneficiário.csv',
              delim = ';', header = true, encoding = 'latin-1', all_varchar = true);

CREATE OR REPLACE TABLE stg_detalhe AS
SELECT
    CAST("Ano-calendário" AS INTEGER)                             AS ano,
    CNPJ                                                          AS cnpj,
    trim("Tipo Renúncia")                                         AS tipo_renuncia,
    trim("Benefício Fiscal")                                      AS beneficio_fiscal,
    trim(Tributo)                                                 AS tributo,
    trim("Fundamento Legal")                                      AS fundamento_legal,
    CAST(replace("Valor Renúncia Fiscal (R$)", ',', '.') AS DOUBLE) AS valor
FROM read_csv('data/raw/*/*_RenúnciasFiscais.csv',
              delim = ';', header = true, encoding = 'latin-1', all_varchar = true);

-- ------------------------------------------------------------------ macro --

CREATE OR REPLACE TABLE macro_ipca AS
SELECT CAST(ano AS INTEGER) ano, CAST(ipca_indice_medio AS DOUBLE) ipca_indice_medio
FROM read_csv('data/macro/ipca.csv', header = true);

CREATE OR REPLACE TABLE macro_pib AS
SELECT CAST(ano AS INTEGER) ano, CAST(pib_nominal_reais AS DOUBLE) pib_nominal_reais
FROM read_csv('data/macro/pib.csv', header = true);

-- ------------------------------------------------------------- dimensões --

-- Seções da CNAE 2.0 derivadas da divisão (2 primeiros dígitos do código).
CREATE OR REPLACE TABLE dim_cnae AS
WITH base AS (
    SELECT cnae,
           any_value(cnae_desc)                AS descricao,
           substr(cnae, 1, 2)                  AS divisao
    FROM stg_beneficiario
    GROUP BY cnae
),
sec AS (
    SELECT *,
        CASE
            WHEN divisao = '00'                       THEN 'Z'
            WHEN divisao BETWEEN '01' AND '03'        THEN 'A'
            WHEN divisao BETWEEN '05' AND '09'        THEN 'B'
            WHEN divisao BETWEEN '10' AND '33'        THEN 'C'
            WHEN divisao = '35'                       THEN 'D'
            WHEN divisao BETWEEN '36' AND '39'        THEN 'E'
            WHEN divisao BETWEEN '41' AND '43'        THEN 'F'
            WHEN divisao BETWEEN '45' AND '47'        THEN 'G'
            WHEN divisao BETWEEN '49' AND '53'        THEN 'H'
            WHEN divisao BETWEEN '55' AND '56'        THEN 'I'
            WHEN divisao BETWEEN '58' AND '63'        THEN 'J'
            WHEN divisao BETWEEN '64' AND '66'        THEN 'K'
            WHEN divisao = '68'                       THEN 'L'
            WHEN divisao BETWEEN '69' AND '75'        THEN 'M'
            WHEN divisao BETWEEN '77' AND '82'        THEN 'N'
            WHEN divisao = '84'                       THEN 'O'
            WHEN divisao = '85'                       THEN 'P'
            WHEN divisao BETWEEN '86' AND '88'        THEN 'Q'
            WHEN divisao BETWEEN '90' AND '93'        THEN 'R'
            WHEN divisao BETWEEN '94' AND '96'        THEN 'S'
            WHEN divisao = '97'                       THEN 'T'
            WHEN divisao = '99'                       THEN 'U'
            ELSE 'Z'
        END AS secao
    FROM base
)
SELECT cnae, descricao, divisao, secao,
    CASE secao
        WHEN 'A' THEN 'Agropecuária e extração vegetal'
        WHEN 'B' THEN 'Indústrias extrativas'
        WHEN 'C' THEN 'Indústria de transformação'
        WHEN 'D' THEN 'Eletricidade e gás'
        WHEN 'E' THEN 'Água, esgoto e resíduos'
        WHEN 'F' THEN 'Construção'
        WHEN 'G' THEN 'Comércio e reparação de veículos'
        WHEN 'H' THEN 'Transporte, armazenagem e correio'
        WHEN 'I' THEN 'Alojamento e alimentação'
        WHEN 'J' THEN 'Informação e comunicação'
        WHEN 'K' THEN 'Atividades financeiras e seguros'
        WHEN 'L' THEN 'Atividades imobiliárias'
        WHEN 'M' THEN 'Atividades profissionais e técnicas'
        WHEN 'N' THEN 'Atividades administrativas'
        WHEN 'O' THEN 'Administração pública'
        WHEN 'P' THEN 'Educação'
        WHEN 'Q' THEN 'Saúde humana e serviços sociais'
        WHEN 'R' THEN 'Artes, cultura, esporte e recreação'
        WHEN 'S' THEN 'Outras atividades de serviços'
        WHEN 'T' THEN 'Serviços domésticos'
        WHEN 'U' THEN 'Organismos internacionais'
        ELSE          'Sem informação'
    END AS secao_nome
FROM sec;

-- Um registro por CNPJ (estabelecimento). Nome e cadastro do ano mais recente.
CREATE OR REPLACE TABLE dim_estab AS
SELECT
    row_number() OVER (ORDER BY cnpj) - 1              AS estab_id,
    cnpj,
    substr(cnpj, 1, 8)                                 AS cnpj_raiz,
    arg_max(razao_social, ano)                         AS razao_social,
    arg_max(nome_fantasia, ano)                        AS nome_fantasia,
    arg_max(cnae, ano)                                 AS cnae,
    arg_max(municipio, ano)                            AS municipio,
    arg_max(uf, ano)                                   AS uf,
    sum(valor)                                         AS valor_total,
    min(ano)                                           AS primeiro_ano,
    max(ano)                                           AS ultimo_ano
FROM stg_beneficiario
GROUP BY cnpj;

-- Grupo econômico = raiz do CNPJ (8 primeiros dígitos). Nome e CNAE herdados
-- do estabelecimento de maior valor acumulado, não da matriz — a matriz muitas
-- vezes é holding com CNAE genérico.
CREATE OR REPLACE TABLE dim_grupo AS
SELECT
    cnpj_raiz,
    arg_max(razao_social, valor_total)                 AS nome_grupo,
    arg_max(cnae, valor_total)                         AS cnae_principal,
    arg_max(uf, valor_total)                           AS uf_principal,
    arg_max(municipio, valor_total)                    AS municipio_principal,
    count(*)                                           AS n_estab,
    sum(valor_total)                                   AS valor_total,
    min(primeiro_ano)                                  AS primeiro_ano,
    max(ultimo_ano)                                    AS ultimo_ano
FROM dim_estab
GROUP BY cnpj_raiz;

-- O "regime" é o mecanismo jurídico por trás da renúncia. Para o IRPJ/CSLL
-- declarado, o próprio campo Benefício Fiscal já nomeia o programa; para as
-- renúncias de importação, o mecanismo só aparece no Fundamento Legal, e é dele
-- que a classificação abaixo é extraída. Regras explícitas, com balde residual
-- nomeado — o fundamento original fica sempre visível ao lado.
CREATE OR REPLACE MACRO regime_de(tipo, benef, fund) AS (
  CASE
    WHEN tipo LIKE 'Declarado%' THEN
      CASE
        WHEN benef LIKE 'Sudam/Sudene%'       THEN 'Sudam/Sudene'
        WHEN benef LIKE 'Prouni%'             THEN 'Prouni'
        WHEN benef LIKE '%Perse%'             THEN 'Perse (setor de eventos)'
        WHEN benef LIKE 'Programa Rota 2030%' THEN 'Rota 2030'
        WHEN benef LIKE 'Pronac%'             THEN 'Lei Rouanet (Pronac)'
        WHEN benef LIKE 'Programa de Alimentação%' THEN 'PAT (alimentação do trabalhador)'
        WHEN benef LIKE 'Fundos de Direitos da Criança%' THEN 'Fundos da Criança e do Adolescente'
        WHEN benef LIKE 'Atividade Audiovisual%'  THEN 'Atividade audiovisual'
        WHEN benef LIKE 'Pronon%'             THEN 'Pronon (oncologia)'
        WHEN benef LIKE 'Pronas%'             THEN 'Pronas/PCD (pessoa com deficiência)'
        WHEN benef LIKE 'Padis%'              THEN 'Padis (semicondutores)'
        WHEN benef LIKE 'Finor%' OR benef LIKE 'Finam%' THEN 'Finor/Finam'
        ELSE benef
      END
    WHEN lower(strip_accents(fund)) LIKE '%repetro%'   THEN 'Repetro (petróleo e gás)'
    WHEN lower(strip_accents(fund)) LIKE '%recof%'     THEN 'Recof (entreposto industrial)'
    WHEN lower(strip_accents(fund)) LIKE '%drawback%'  THEN 'Drawback'
    WHEN lower(strip_accents(fund)) LIKE '%zona franca%'
      OR lower(strip_accents(fund)) LIKE '% zfm%'
      OR lower(strip_accents(fund)) LIKE '%eizof%'
      OR lower(strip_accents(fund)) LIKE '%amazonia ocidental%' THEN 'Zona Franca de Manaus'
    WHEN lower(strip_accents(fund)) LIKE '%loja franca%' THEN 'Loja franca'
    WHEN lower(strip_accents(fund)) LIKE '%entreposto%'
      OR lower(strip_accents(fund)) LIKE '%deposito%'  THEN 'Entreposto e depósito aduaneiro'
    WHEN lower(strip_accents(fund)) LIKE '%admissao temporaria%'
      OR lower(strip_accents(fund)) LIKE '%exportacao temporaria%'
      OR lower(strip_accents(fund)) LIKE '%reimportacao%'
      OR lower(strip_accents(fund)) LIKE '%retornaveis%'   THEN 'Admissão temporária'
    WHEN lower(strip_accents(fund)) LIKE '%reidi%'     THEN 'Reidi (infraestrutura)'
    WHEN lower(strip_accents(fund)) LIKE '%reporto%'   THEN 'Reporto (portos)'
    WHEN lower(strip_accents(fund)) LIKE '%recap%'     THEN 'Recap (exportadoras)'
    WHEN lower(strip_accents(fund)) LIKE '%repes%'     THEN 'Repes (software)'
    WHEN lower(strip_accents(fund)) LIKE '%padis%' OR lower(strip_accents(fund)) LIKE '%patvd%'
      THEN 'Padis (semicondutores)'
    WHEN lower(strip_accents(fund)) LIKE '%aeronave%' OR lower(strip_accents(fund)) LIKE '%aeronautic%'
      THEN 'Setor aeronáutico'
    WHEN lower(strip_accents(fund)) LIKE '%embarcac%' OR lower(strip_accents(fund)) LIKE '%reb %'
      OR lower(strip_accents(fund)) LIKE '%portuaria%'     THEN 'Setor naval e portuário'
    WHEN lower(strip_accents(fund)) LIKE '%autopec%' OR lower(strip_accents(fund)) LIKE '%tratores%'
      OR lower(strip_accents(fund)) LIKE '%colheitadeiras%' THEN 'Autopeças e máquinas agrícolas'
    WHEN lower(strip_accents(fund)) LIKE '%farmaceutic%' OR lower(strip_accents(fund)) LIKE '%3002%'
      OR lower(strip_accents(fund)) LIKE '%quimicos%'      THEN 'Farmacêuticos e químicos'
    WHEN lower(strip_accents(fund)) LIKE '%adubos%' OR lower(strip_accents(fund)) LIKE '%fertilizantes%'
      OR lower(strip_accents(fund)) LIKE '%defensivos%' OR lower(strip_accents(fund)) LIKE '%trigo%'
      OR lower(strip_accents(fund)) LIKE '%leite%' OR lower(strip_accents(fund)) LIKE '%queijo%'
      OR lower(strip_accents(fund)) LIKE '%feijoes%' OR lower(strip_accents(fund)) LIKE '%sementes%'
      OR lower(strip_accents(fund)) LIKE '%horticulas%' OR lower(strip_accents(fund)) LIKE '%massas alimenticias%'
      OR lower(strip_accents(fund)) LIKE '%vacinas para medicina%'
      OR lower(strip_accents(fund)) LIKE '%lei 10925/04%'  THEN 'Desoneração de alimentos e insumos agrícolas'
    WHEN lower(strip_accents(fund)) LIKE '%gas natural%' OR lower(strip_accents(fund)) LIKE '%termeletricas%'
      THEN 'Gás natural e energia'
    WHEN lower(strip_accents(fund)) LIKE '%cientistas%' OR lower(strip_accents(fund)) LIKE '%pesquisador%'
      OR lower(strip_accents(fund)) LIKE '%cnpq%'          THEN 'Ciência e pesquisa'
    WHEN lower(strip_accents(fund)) LIKE '%uniao, estados%' OR lower(strip_accents(fund)) LIKE '%autarquias%'
      OR lower(strip_accents(fund)) LIKE '%diplomatic%'
      OR lower(strip_accents(fund)) LIKE '%organismos internacionais%'
      THEN 'Entes públicos e organismos internacionais'
    WHEN lower(strip_accents(fund)) LIKE '%contingenciamento%' OR lower(strip_accents(fund)) LIKE '%ace 14%'
      OR lower(strip_accents(fund)) LIKE '%protocolo adicional%' THEN 'Acordos comerciais e cotas'
    WHEN lower(strip_accents(fund)) LIKE '%livros%'      THEN 'Livros e imprensa'
    WHEN lower(strip_accents(fund)) LIKE '%regimes aduaneiros especiais%'
      THEN 'Regimes aduaneiros especiais (PIS/Cofins)'
    WHEN lower(strip_accents(fund)) LIKE '%outras isencoes%' THEN 'Outras isenções não capituladas'
    ELSE 'Outros fundamentos de importação'
  END
);

-- Grão mais fino que a origem oferece: benefício × fundamento legal.
CREATE OR REPLACE TABLE dim_item AS
SELECT
    row_number() OVER (ORDER BY tipo_renuncia, beneficio_fiscal, fundamento_legal) - 1 AS item_id,
    tipo_renuncia,
    CASE
        WHEN tipo_renuncia LIKE 'Declarado%' THEN 'IRPJ/CSLL declarado'
        WHEN tipo_renuncia LIKE 'Imposto de Importação%' THEN 'Importação: II e IPI'
        ELSE 'Importação: PIS/Cofins'
    END AS tipo_curto,
    beneficio_fiscal, tributo, fundamento_legal,
    regime_de(tipo_renuncia, beneficio_fiscal, fundamento_legal) AS regime,
    sum(valor) AS valor_total
FROM stg_detalhe
GROUP BY tipo_renuncia, beneficio_fiscal, tributo, fundamento_legal;

-- ----------------------------------------------------------------- fatos --

CREATE OR REPLACE TABLE fato_empresa_ano AS
SELECT e.estab_id, s.ano, sum(s.valor) AS valor
FROM stg_beneficiario s
JOIN dim_estab e USING (cnpj)
GROUP BY e.estab_id, s.ano;

CREATE OR REPLACE TABLE fato_item_ano AS
SELECT e.estab_id, d.ano, i.item_id, sum(d.valor) AS valor
FROM stg_detalhe d
JOIN dim_estab e USING (cnpj)
JOIN dim_item  i USING (tipo_renuncia, beneficio_fiscal, tributo, fundamento_legal)
GROUP BY e.estab_id, d.ano, i.item_id;

-- ----------------------------------------------------------------- marts --

CREATE OR REPLACE VIEW v_empresa_ano AS
SELECT f.ano, f.valor, e.estab_id, e.cnpj, e.cnpj_raiz, e.razao_social,
       e.nome_fantasia, e.uf, e.municipio, c.cnae, c.descricao AS cnae_desc,
       c.secao, c.secao_nome
FROM fato_empresa_ano f
JOIN dim_estab e USING (estab_id)
JOIN dim_cnae  c ON c.cnae = e.cnae;

CREATE OR REPLACE TABLE mart_ano AS
WITH t AS (
    SELECT ano, sum(valor) valor, count(DISTINCT cnpj) n_estab, count(DISTINCT cnpj_raiz) n_grupos
    FROM v_empresa_ano GROUP BY ano
),
g AS (
    SELECT ano, cnpj_raiz, sum(valor) v FROM v_empresa_ano GROUP BY 1, 2
),
conc AS (
    SELECT g.ano,
           sum(power(g.v / t.valor, 2)) * 10000                                  AS hhi,
           sum(CASE WHEN rn <= 10  THEN g.v END) / max(t.valor)                  AS share_top10,
           sum(CASE WHEN rn <= 100 THEN g.v END) / max(t.valor)                  AS share_top100
    FROM (SELECT *, row_number() OVER (PARTITION BY ano ORDER BY v DESC) rn FROM g) g
    JOIN t USING (ano)
    GROUP BY g.ano
)
SELECT t.ano, t.valor, t.n_estab, t.n_grupos,
       i.ipca_indice_medio, p.pib_nominal_reais,
       t.valor / p.pib_nominal_reais * 100 AS pct_pib,
       c.hhi, c.share_top10, c.share_top100
FROM t
LEFT JOIN macro_ipca i USING (ano)
LEFT JOIN macro_pib  p USING (ano)
LEFT JOIN conc       c USING (ano)
ORDER BY t.ano;

CREATE OR REPLACE TABLE mart_setor_ano AS
SELECT secao, any_value(secao_nome) secao_nome, ano,
       sum(valor) valor, count(DISTINCT cnpj_raiz) n_grupos
FROM v_empresa_ano GROUP BY secao, ano;

CREATE OR REPLACE TABLE mart_uf_ano AS
SELECT uf, ano, sum(valor) valor, count(DISTINCT cnpj_raiz) n_grupos
FROM v_empresa_ano GROUP BY uf, ano;

CREATE OR REPLACE TABLE mart_item_ano AS
SELECT i.item_id, i.tipo_curto, i.beneficio_fiscal, i.tributo, i.regime, i.fundamento_legal, f.ano,
       sum(f.valor) valor, count(DISTINCT f.estab_id) n_estab
FROM fato_item_ano f JOIN dim_item i USING (item_id)
GROUP BY 1, 2, 3, 4, 5, 6, 7;

CREATE OR REPLACE TABLE mart_regime_ano AS
SELECT i.regime, f.ano, sum(f.valor) valor, count(DISTINCT e.cnpj_raiz) n_grupos
FROM fato_item_ano f JOIN dim_item i USING (item_id) JOIN dim_estab e USING (estab_id)
GROUP BY 1, 2;

-- Cruzamento setor × mecanismo: a matriz de "quem captura o quê".
CREATE OR REPLACE TABLE mart_setor_regime AS
SELECT c.secao, c.secao_nome, i.regime, f.ano,
       sum(f.valor) valor, count(DISTINCT e.cnpj_raiz) n_grupos
FROM fato_item_ano f
JOIN dim_item  i USING (item_id)
JOIN dim_estab e USING (estab_id)
JOIN dim_cnae  c ON c.cnae = e.cnae
GROUP BY 1, 2, 3, 4;

-- Grupo × ano com as métricas de outlier. Tudo em log: a distribuição de
-- renúncia tem cauda longa demais para z-score em nível fazer sentido.
CREATE OR REPLACE TABLE mart_grupo_ano AS
WITH ga AS (
    SELECT cnpj_raiz, ano, sum(valor) valor,
           any_value(secao) secao, any_value(secao_nome) secao_nome
    FROM v_empresa_ano GROUP BY cnpj_raiz, ano
),
tot AS (SELECT ano, sum(valor) valor_ano FROM ga GROUP BY ano),
tots AS (SELECT ano, secao, sum(valor) valor_setor_ano FROM ga GROUP BY ano, secao),

-- z robusto contra a própria história do grupo
hist_med AS (
    SELECT cnpj_raiz, median(ln(valor)) med, count(*) n_anos
    FROM ga WHERE valor > 0 GROUP BY cnpj_raiz
),
hist_mad AS (
    SELECT g.cnpj_raiz, median(abs(ln(g.valor) - h.med)) mad
    FROM ga g JOIN hist_med h USING (cnpj_raiz) WHERE g.valor > 0
    GROUP BY g.cnpj_raiz
),
-- z robusto contra os demais grupos da mesma seção no mesmo ano
sec_med AS (
    SELECT ano, secao, median(ln(valor)) med, count(*) n
    FROM ga WHERE valor > 0 GROUP BY ano, secao
),
sec_mad AS (
    SELECT g.ano, g.secao, median(abs(ln(g.valor) - s.med)) mad
    FROM ga g JOIN sec_med s USING (ano, secao) WHERE g.valor > 0
    GROUP BY g.ano, g.secao
)
SELECT
    g.cnpj_raiz, g.ano, g.valor, g.secao, g.secao_nome,
    row_number() OVER (PARTITION BY g.ano ORDER BY g.valor DESC)          AS rank_ano,
    g.valor / t.valor_ano                                                 AS share_ano,
    g.valor / ts.valor_setor_ano                                          AS share_setor_ano,
    lag(g.valor) OVER (PARTITION BY g.cnpj_raiz ORDER BY g.ano)           AS valor_ant,
    g.valor - lag(g.valor) OVER (PARTITION BY g.cnpj_raiz ORDER BY g.ano) AS d_yoy,
    CASE WHEN lag(g.valor) OVER (PARTITION BY g.cnpj_raiz ORDER BY g.ano) > 0
         THEN g.valor / lag(g.valor) OVER (PARTITION BY g.cnpj_raiz ORDER BY g.ano) - 1
    END                                                                   AS pct_yoy,
    hm.n_anos,
    CASE WHEN hm.n_anos >= 4 AND hd.mad > 0 AND g.valor > 0
         THEN (ln(g.valor) - hm.med) / (1.4826 * hd.mad) END              AS z_hist,
    CASE WHEN sm.n >= 20 AND sd.mad > 0 AND g.valor > 0
         THEN (ln(g.valor) - sm.med) / (1.4826 * sd.mad) END              AS z_setor,
    (g.ano = dg.primeiro_ano AND g.ano > 2015)                            AS estreia
FROM ga g
JOIN tot  t  USING (ano)
JOIN tots ts ON ts.ano = g.ano AND ts.secao = g.secao
JOIN dim_grupo dg USING (cnpj_raiz)
LEFT JOIN hist_med hm USING (cnpj_raiz)
LEFT JOIN hist_mad hd USING (cnpj_raiz)
LEFT JOIN sec_med  sm ON sm.ano = g.ano AND sm.secao = g.secao
LEFT JOIN sec_mad  sd ON sd.ano = g.ano AND sd.secao = g.secao;
