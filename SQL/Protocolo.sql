-- Query de identificação dos casos a protocolar
                    
                           Select t.id_tramitacao, REPLACE(p.numero_processo, 'TESTE', '') AS numero_processo, 
                CASE 
                WHEN p.numero_processo like '%8.04%' THEN 
                    'https://projudi.tjam.jus.br/projudi/'
                ELSE '' END AS TRIBUNAL, ev.descricao as evento, Qd.total_arquivos, gp.descricao, ag_data_hora
                from `views-nogueiravasc-cpj`.tramitacao t 
                left join `views-nogueiravasc-cpj`.cad_processo p on p.pj = t.id_processo
                left join `views-nogueiravasc-cpj`.tramitacao_situacao s on s.id_tramitacao_situacao = t.id_tramitacao_situacao
                left join `views-nogueiravasc-cpj`.tab_evento ev on ev.sigla = t.evento
                inner join `views-nogueiravasc-cpj`.tramitacao_documentos Qd on Qd.Id_tramitacao = t.id_tramitacao
                inner join `views-nogueiravasc-cpj`.tab_grupo_trabalho gp on gp.codigo = p.grupo_trabalho
                where t.evento in 
                    ('PPTR','PPAC', 'PPT', 'PPOP', 'PPOF', 'PTCD', 'PEEX', 'PPTM', 'PPCO', 'PPME', 'PPL', 'PPEM', 'PTCF', 'PTCI', 'PPEP', 'PPTCZ')
                    and Qd.total_arquivos > 0
                    and s.descricao = 'Pendente'
                    and p.numero_processo like'%8.04%'
                    and CASE 
                    WHEN p.numero_processo like '%8.04%' THEN 
                        'https://projudi.tjam.jus.br/projudi/'
                    ELSE '' END <> ''
                    and gp.codigo not in (123,130)
                    and t.ag_data_hora <= current_date() 
                           
                    group by t.id_tramitacao 
                    ORDER BY t.id_tramitacao ASC
               