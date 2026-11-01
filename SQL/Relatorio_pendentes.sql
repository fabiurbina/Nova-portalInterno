
				-- Query de identificação dos casos a protocolar
				Select
                t.id_tramitacao, 
				ltrim(rtrim(p.numero_processo)) as numero_processo, 
				ev.descricao, 
				t.evento,
                gp.codigo,
				gp.descricao,
				s.descricao as sitiacao,
				t.cumprido_por,
				t.cumprido_em,
                t.ag_data_hora,
                t.id_pessoa_solicitada,
                pes.nome
				from `views-nogueiravasc-cpj`.tramitacao t 
				left join `views-nogueiravasc-cpj`.cad_processo p on p.pj = t.id_processo
				left join `views-nogueiravasc-cpj`.tramitacao_situacao s on s.id_tramitacao_situacao = t.id_tramitacao_situacao
				left join `views-nogueiravasc-cpj`.tab_evento ev on ev.sigla = t.evento
				left join `views-nogueiravasc-cpj`.tab_grupo_trabalho gp on gp.codigo = p.grupo_trabalho
				left join `views-nogueiravasc-cpj`.cad_pessoa pes on pes.codigo = t.id_pessoa_solicitada
				-- left join `views-nogueiravasc-cpj`.usuario u on u.id_usuario = t.cumprido_por
				where s.descricao = 'Pendente' 
                and t.evento <> 'ANP'
                AND CAST(t.ag_data_hora AS DATE) BETWEEN DATE_SUB(CURDATE(), INTERVAL 1 YEAR) AND CURDATE()