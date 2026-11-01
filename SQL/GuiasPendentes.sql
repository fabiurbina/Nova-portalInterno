 				
                Select  count(*) as qtd, 'Diligência' as evento
                from tramitacao t
				inner join tab_evento ev on ev.sigla = t.evento
				left join cad_processo p on p.pj = t.id_processo
				left join tramitacao_situacao s on s.id_tramitacao_situacao = t.id_tramitacao_situacao
				left join tab_grupo_trabalho gp on gp.codigo = p.grupo_trabalho
				LEFT JOIN cad_pessoa cp on cp.codigo = p.primeiro_autor
				LEFT JOIN cad_pessoa reu on reu.codigo = p.primeiro_reu
				LEFT JOIN (
				SELECT
					t.ag_data_hora,
					t.id_processo,
					t.texto,
					t.id_tramitacao,
					s.descricao,
					t.cumprido_em,
					ROW_NUMBER() OVER (
						PARTITION BY t.id_processo
						ORDER BY t.cumprido_em DESC
					) AS rn
				FROM tramitacao t
				INNER JOIN tramitacao_situacao s
					ON s.id_tramitacao_situacao = t.id_tramitacao_situacao
				WHERE t.evento = 'ADILI'
				AND s.descricao = 'Concluído'
			) relat
				ON relat.id_processo = p.pj
			AND relat.rn = 1 
				LEFT JOIN tab_juizo j on p.juizo = j.sigla
				left join (select * from tramitacao tt where tt.evento = 'VPCON' AND tt.id_tramitacao_situacao = 0) vpcon on vpcon.id_processo = p.pj       
				
				where t.evento in ('EGAR','EMDES','EMGE','GAI',
				'GAP','GCD','GCFI','GIM','GCI','GCC','GAIN','GCCF','GHP','GRI')
				and s.descricao = 'Pendente'
				and ev.descricao = 'GUIA CUSTAS DILIGÊNCIA'
				and replace(relat.texto,' ','') like '%(X)%'
				and t.ag_data_hora = current_date()
				
                union all
                
                Select count(*) as Qtd, 'Recurso Inominado'
                from tramitacao t
                inner join tab_evento ev on ev.sigla = t.evento
                left join cad_processo p on p.pj = t.id_processo
                left join tramitacao_situacao s on s.id_tramitacao_situacao = t.id_tramitacao_situacao
                left join tab_grupo_trabalho gp on gp.codigo = p.grupo_trabalho
                LEFT JOIN cad_pessoa cp on cp.codigo = p.primeiro_autor
                LEFT JOIN cad_pessoa reu on reu.codigo = p.primeiro_reu
                LEFT JOIN tab_juizo j on j.sigla = p.juizo   

                where t.evento in ('GMS', 'GAT', 'GEE', 'GRI', 'GIM', 'GAP', 'GRE', 
                'GHP', 'GAIN', 'GDJ', 'GRA', 'EMDES', 'GFI', 'GAI', 'GPR', 'GEX', 
                'GRO', 'GCD', 'EGAR', 'GCCF', 'RFG', 'GCC', 'EMGE', 'GCI', 'GCFI') 
                and s.descricao = 'Pendente'
                and ev.descricao = 'GUIA RECURSO INOMINADO'
				and t.ag_data_hora <= current_date()
                
				union all 
                
                 Select count(*) as Qtd, 'Recurso Apelação'
                from tramitacao t
                inner join tab_evento ev on ev.sigla = t.evento
                left join cad_processo p on p.pj = t.id_processo
                left join tramitacao_situacao s on s.id_tramitacao_situacao = t.id_tramitacao_situacao
                left join tab_grupo_trabalho gp on gp.codigo = p.grupo_trabalho
                LEFT JOIN cad_pessoa cp on cp.codigo = p.primeiro_autor
                LEFT JOIN cad_pessoa reu on reu.codigo = p.primeiro_reu
                LEFT JOIN tab_juizo j on j.sigla = p.juizo 

                where evento in ('GMS', 'GAT', 'GEE', 'GRI', 'GIM', 'GAP', 'GRE', 
                'GHP', 'GAIN', 'GDJ', 'GRA', 'EMDES', 'GFI', 'GAI', 'GPR', 'GEX', 
                'GRO', 'GCD', 'EGAR', 'GCCF', 'RFG', 'GCC', 'EMGE', 'GCI', 'GCFI') 
                and s.descricao = 'Pendente'
                and ev.descricao = 'GUIA APELAÇÃO'
                and t.ag_data_hora <= current_date()
                
				Union all 
                
                 Select count(*) as qtd, 'Recurso Especial'
            from tramitacao t
            inner join tab_evento ev on ev.sigla = t.evento
            left join cad_processo p on p.pj = t.id_processo
            left join tramitacao_situacao s on s.id_tramitacao_situacao = t.id_tramitacao_situacao
            left join tab_grupo_trabalho gp on gp.codigo = p.grupo_trabalho
            LEFT JOIN cad_pessoa cp on cp.codigo = p.primeiro_autor
            LEFT JOIN cad_pessoa reu on reu.codigo = p.primeiro_reu
            LEFT JOIN tab_juizo j on j.sigla = p.juizo   
            where evento in ('GMS', 'GAT', 'GEE', 'GRI', 'GIM', 'GAP', 'GRE', 
                'GHP', 'GAIN', 'GDJ', 'GRA', 'EMDES', 'GFI', 'GAI', 'GPR', 'GEX', 
                'GRO', 'GCD', 'EGAR', 'GCCF', 'RFG', 'GCC', 'EMGE', 'GCI', 'GCFI') 
                and s.descricao = 'Pendente'
                and ev.descricao = 'GUIA RECURSO ESPECIAL'
                and t.ag_data_hora <= current_date()
