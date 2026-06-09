with orders as (

    select * from {{ ref('stg_orders') }}

),

order_items as (

    select
        order_id,
        count(*)                                as basket_size,
        sum(is_reordered)                       as reordered_item_count,
        round(avg(cart_position)::numeric, 2)   as avg_cart_position
    from {{ ref('stg_order_products') }}
    group by order_id

)

select
    o.order_id,
    o.user_id,
    o.dataset_split,
    o.order_number,
    o.order_day_of_week,
    o.order_day_name,
    o.order_hour,
    o.days_since_prior_order,
    coalesce(i.basket_size, 0)                  as basket_size,
    coalesce(i.reordered_item_count, 0)         as reordered_item_count,
    coalesce(i.avg_cart_position, 0)            as avg_cart_position,
    case
        when coalesce(i.basket_size, 0) > 0
        then round(
            coalesce(i.reordered_item_count, 0)::numeric
            / i.basket_size, 4)
        else 0
    end                                         as reorder_rate
from orders o
left join order_items i on o.order_id = i.order_id