with tab as (
  select 开单部门id,
         时间,
         '整复次数' 项目,
         1 子序号,
         count(distinct 病人id) 人次,
         sum(数次) 数次
    from (select 病人科室id 开单部门id,
                 病人id,
                 max(数次) as 数次,
                 trunc(登记时间, 'month') 时间
            from 门诊费用记录 a,
                 收费项目目录 b,
                 收费分类目录 c
           where a.收费细目id = b.id
             and b.分类id = c.id
             and 记录状态 <> 0
             and (c.id = 264 or b.名称 like '石膏固定术%')
           group by 病人科室id, 病人id, 登记时间)
   group by 开单部门id, 时间
  union all
  select 开单部门id,
         时间,
         '筋伤次数' 项目,
         2 子序号,
         count(distinct 病人id) 人次,
         sum(数次) 数次
    from (select 病人科室id 开单部门id,
                 病人id,
                 max(数次) as 数次,
                 trunc(登记时间, 'month') 时间
            from 门诊费用记录 a,
                 收费项目目录 b,
                 收费分类目录 c
           where a.收费细目id = b.id
             and b.分类id = c.id
             and 记录状态 <> 0
             and b.id = 2648
           group by 病人科室id, 病人id, 登记时间)
   group by 开单部门id, 时间
  union all
  select 开单部门id,
         时间,
         '针灸次数' 项目,
         3 子序号,
         count(distinct 病人id) 人次,
         sum(数次) 数次
    from (select 病人科室id 开单部门id,
                 病人id,
                 max(数次) as 数次,
                 trunc(登记时间, 'month') 时间
            from 门诊费用记录 a,
                 收费项目目录 b,
                 收费分类目录 c
           where a.收费细目id = b.id
             and b.分类id = c.id
             and 记录状态 <> 0
             and c.id = 59
           group by 病人科室id, 病人id, 登记时间)
   group by 开单部门id, 时间
  union all
  select 开单部门id,
         时间,
         '推拿次数' 项目,
         4 子序号,
         count(distinct 病人id) 人次,
         sum(数次) 数次
    from (select 病人科室id 开单部门id,
                 病人id,
                 max(数次) as 数次,
                 trunc(登记时间, 'month') 时间
            from 门诊费用记录 a,
                 收费项目目录 b,
                 收费分类目录 c
           where a.收费细目id = b.id
             and b.分类id = c.id
             and 记录状态 <> 0
             and c.id = 60
           group by 病人科室id, 病人id, 登记时间)
   group by 开单部门id, 时间
  union all
  select 开单部门id,
         时间,
         '康复次数' 项目,
         5 子序号,
         count(distinct 病人id) 人次,
         sum(数次) 数次
    from (select 病人科室id 开单部门id,
                 病人id,
                 max(数次) as 数次,
                 trunc(登记时间, 'month') 时间
            from 门诊费用记录 a,
                 收费项目目录 b,
                 收费分类目录 c
           where a.收费细目id = b.id
             and b.分类id = c.id
             and 记录状态 <> 0
             and c.id = 57
           group by 病人科室id, 病人id, 登记时间)
   group by 开单部门id, 时间
  union all
  select 开单部门id,
         时间,
         '中药人次' 项目,
         6 子序号,
         count(distinct 病人id) 人次,
         count(distinct 病人id) 数次
    from (select distinct 病人科室id 开单部门id,
                          病人id,
                          trunc(登记时间, 'month') 时间
            from 门诊费用记录 a, 收费项目目录 b
           where a.收费细目id = b.id
             and 记录状态 <> 0
             and 收费类别 in ('6','7'))
   group by 开单部门id, 时间
),
-- 挂号人次（按科室）
gh as (
  select 执行部门id 科室id,
         sum(decode(记录状态,1,1,3,1,2,-1)) 人次
    from 病人挂号记录
   where 发生时间 between [0] and [1]
     and 记录状态 <> 0
   group by 执行部门id
  having sum(decode(记录状态,1,1,3,1,2,-1)) <> 0
)
select 科室, 项目, 人次, 数次
  from (
    -- 各科室明细
    select 1 序号,
           b.名称 科室,
           a.子序号,
           a.项目,
           sum(a.人次) as 人次,
           sum(a.数次) as 数次
      from tab a, 部门表 b
     where a.开单部门id = b.id
       and a.时间 between [0] and [1]
     group by b.名称, a.项目, a.子序号
    union all
    -- 各科室中医治疗参与率
    select 1 序号,
           b.名称 科室,
           7 子序号,
           '中医治疗参与率' 项目,
           least(round(a.人次 / c.人次 * 100, 2), 100) 人次,
           least(round(a.人次 / c.人次 * 100, 2), 100) 数次
      from (select 开单部门id, sum(人次) 人次
              from tab
             where 时间 between [0] and [1]
             group by 开单部门id) a,
           部门表 b,
           gh c
     where a.开单部门id = b.id
       and a.开单部门id = c.科室id
    union all
    -- 各科室非药物治疗参与率
    select 1 序号,
           b.名称 科室,
           8 子序号,
           '非药物治疗参与率' 项目,
           least(round(a.人次 / c.人次 * 100, 2), 100) 人次,
           least(round(a.人次 / c.人次 * 100, 2), 100) 数次
      from (select 开单部门id,
                   sum(case when 项目 = '中药人次' then 0 else 人次 end) 人次
              from tab
             where 时间 between [0] and [1]
             group by 开单部门id) a,
           部门表 b,
           gh c
     where a.开单部门id = b.id
       and a.开单部门id = c.科室id
    union all
    -- 总合计明细
    select 2 序号,
           '总合计' 科室,
           a.子序号,
           a.项目,
           sum(a.人次) 人次,
           sum(a.数次) 数次
      from tab a
     where a.时间 between [0] and [1]
     group by a.项目, a.子序号
    union all
    -- 总合计中医治疗参与率
    select 2 序号,
           '总合计' 科室,
           7 子序号,
           '中医治疗参与率' 项目,
           round(sum(a.人次) / sum(c.人次) * 100, 2) 人次,
           round(sum(a.人次) / sum(c.人次) * 100, 2) 数次
      from (select 开单部门id, sum(人次) 人次
              from tab
             where 时间 between [0] and [1]
             group by 开单部门id) a,
           gh c
     where a.开单部门id = c.科室id
    union all
    -- 总合计非药物治疗参与率
    select 2 序号,
           '总合计' 科室,
           8 子序号,
           '非药物治疗参与率' 项目,
           round(sum(a.人次) / sum(c.人次) * 100, 2) 人次,
           round(sum(a.人次) / sum(c.人次) * 100, 2) 数次
      from (select 开单部门id,
                   sum(case when 项目 = '中药人次' then 0 else 人次 end) 人次
              from tab
             where 时间 between [0] and [1]
             group by 开单部门id) a,
           gh c
     where a.开单部门id = c.科室id
)
order by 序号, 科室, 子序号
