SELECT count(*) as qdd, 
s.descricao, 
t.evento, ev.descricao FROM tramitacao t
left join tramitacao_situacao s 
on s.id_tramitacao_situacao = 
t.id_tramitacao_situacao 
inner join tab_evento ev on ev.sigla = t.evento
where t.cumprido_por in (831, 846, 872)
and cast(cumprido_em as date) = current_date()
group by s.descricao, t.evento, ev.descricao