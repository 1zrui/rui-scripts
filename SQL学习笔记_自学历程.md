# SQL 自学历程

> 2026-03-23 开始自学

## 已掌握基础

### 1. SELECT 查询
```sql
-- 查询指定列
SELECT 列名1, 列名2 FROM 表名

-- 查询所有列
SELECT * FROM 表名
```

### 2. WHERE 条件
```sql
SELECT * FROM 表名 WHERE 城市 = '北京'
SELECT * FROM 表名 WHERE 年龄 > 25
```

### 3. ORDER BY 排序
```sql
-- 升序（默认）
SELECT * FROM 表名 ORDER BY 列名

-- 降序
SELECT * FROM 表名 ORDER BY 列名 DESC
```

### 4. JOIN 连接
```sql
-- 内连接
SELECT a.列, b.列
FROM 表A a
INNER JOIN 表B b ON a.主键 = b.外键

-- 左连接
SELECT * FROM 表A LEFT JOIN 表B ON 条件
```

### 5. GROUP BY 分组
```sql
SELECT 客户, SUM(金额) AS 总金额
FROM 订单表
GROUP BY 客户
```

---

## 待学习（Oracle 特有）

- [ ] rownum 分页
- [ ] NVL/NVL2 空值处理
- [ ] DECODE 函数
- [ ] CONNECT BY 层级查询
- [ ] TO_DATE 日期处理
- [ ] 绑定变量