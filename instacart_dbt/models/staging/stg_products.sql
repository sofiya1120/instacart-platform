with products as (

    select * from {{ source('raw', 'raw_products') }}

),

departments as (

    select * from {{ source('raw', 'raw_departments') }}

),

aisles as (

    select * from {{ source('raw', 'raw_aisles') }}

)

select
    p.product_id::integer       as product_id,
    p.product_name              as product_name,
    d.department_id::integer    as department_id,
    d.department                as department_name,
    a.aisle_id::integer         as aisle_id,
    a.aisle                     as aisle_name
from products      p
left join departments d on p.department_id::integer = d.department_id::integer
left join aisles      a on p.aisle_id::integer      = a.aisle_id::integer