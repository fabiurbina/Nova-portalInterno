SELECT
    COUNT(*) AS total_concluidos,
    SUM(DATE(t.cumprido_em) = CURRENT_DATE()) AS concluidos_hoje,
    MAX(t.cumprido_em) AS ultima_atividade
FROM `views-nogueiravasc-cpj`.tramitacao t
LEFT JOIN `views-nogueiravasc-cpj`.cad_processo p
    ON p.pj = t.id_processo
LEFT JOIN `views-nogueiravasc-cpj`.tramitacao_situacao s
    ON s.id_tramitacao_situacao = t.id_tramitacao_situacao
INNER JOIN `views-nogueiravasc-cpj`.tab_grupo_trabalho gp
    ON gp.codigo = p.grupo_trabalho
WHERE t.evento IN (
    'PPTR','PPAC','PPT','PPOP','PPOF','PTCD','PEEX','PPTM',
    'PPCO','PPME','PPL','PPEM','PTCF','PTCI','PPEP','PPTCZ'
)
AND s.descricao = 'Concluído'
AND gp.codigo NOT IN (123,130)
AND t.ag_data_hora <= CURRENT_DATE()
AND t.cumprido_por = 831;