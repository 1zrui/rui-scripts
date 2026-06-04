-- 住院患者
select '住院' 来源,
       b.姓名,
       b.住院号,
       b.入院日期,
       b.出院日期,
       a.医嘱内容,
       (select d.诊断描述
          from 病人诊断记录 d
         where d.病人id = a.病人id
           and d.主页id = a.主页id
           and d.诊断次序 = 1
           and d.诊断类型 = 3
           and d.记录来源 = 3) 诊断
  from 病人医嘱记录 a,
       病案主页 b
 where a.病人id = b.病人id
   and a.主页id = b.主页id
   and a.医嘱内容 like '%骨密度%'
   and a.医嘱状态 in (8, 9)
   and a.相关id is null
   and a.开嘱时间 between to_date('2026-01-01', 'yyyy-mm-dd')
                      and to_date('2026-06-30 23:59:59', 'yyyy-mm-dd hh24:mi:ss')
union all
-- 门诊患者
select '门诊' 来源,
       b.姓名,
       null 住院号,
       null 入院日期,
       null 出院日期,
       a.医嘱内容,
       (select max(decode(d.诊断类型, 1, d.诊断描述))
          from 病人诊断记录 d
         where d.病人id = a.病人id
           and d.主页id = b.id
           and d.诊断次序 = 1
           and d.诊断类型 in (1, 11)
           and d.记录来源 = 3) 诊断
  from 病人医嘱记录 a,
       病人挂号记录 b
 where a.病人id = b.病人id
   and a.挂号单 = b.no
   and a.医嘱内容 like '%骨密度%'
   and a.医嘱状态 in (8, 9)
   and a.相关id is null
   and a.病人来源 = 1
   and a.开嘱时间 between to_date('2026-01-01', 'yyyy-mm-dd')
                      and to_date('2026-06-30 23:59:59', 'yyyy-mm-dd hh24:mi:ss')
