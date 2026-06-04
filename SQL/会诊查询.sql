select m.*,p.title,
       p.contenttext,
       extractvalue(p.Content,'//zlxml//element[@title="会诊类型1"]') 会诊类型,
       extractvalue(p.Content,'//zlxml//element[@sid="B515D7E55A4F422A86E46FF567D423AA"]/@value') 会诊到达时间
from (
    select 1 序号, c.名称 科室, a.id 医嘱id
    from 病案主页@hisinterface x,
         病人医嘱记录@hisinterface a,
         部门表@hisinterface c
    where x.病人id = a.病人id
      and x.主页id = a.主页id
      and x.出院科室id = c.id
      and a.医嘱内容 like '%会诊%'
      and x.出院日期 between
          /*B0*/TO_DATE('2026-04-01 00:00:00','YYYY-MM-DD HH24:MI:SS')/*E0*/
      AND
          /*B1*/TO_DATE('2026-04-30 23:59:59','YYYY-MM-DD HH24:MI:SS')/*E1*/
) m,
BZ_ACT_LOG n,
BZ_DOC_LOG p
where m.医嘱id||'' = substr(n.extend_tag,4)
  and n.id = p.actlog_id