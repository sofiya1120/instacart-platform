with order_items as (

    select * from {{ ref('stg_order_products') }}

),

products as (

    select * from {{ ref('stg_products') }}

)

select
    p.product_id,
    p.product_name,
    p.department_name,
    p.aisle_name,
    count(*)                                        as total_orders,
    sum(oi.is_reordered)                            as reorder_count,
    round(avg(oi.cart_position)::numeric, 2)        as avg_cart_position,
    round(
        sum(oi.is_reordered)::numeric
        / nullif(count(*), 0),
        4
    )                                               as reorder_rate
from order_items oi
join products p on oi.product_id = p.product_id
group by
    p.product_id,
    p.product_name,
    p.department_name,
    p.aisle_name