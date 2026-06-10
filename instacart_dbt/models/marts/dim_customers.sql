with fct as (

    select * from {{ ref('fct_orders') }}

),

customer_stats as (

    select
        user_id,
        count(distinct order_id)                    as total_orders,
        round(avg(basket_size)::numeric, 2)         as avg_basket_size,
        round(
            avg(days_since_prior_order)::numeric, 2
        )                                           as avg_days_between_orders,
        round(avg(reorder_rate)::numeric, 4)        as avg_reorder_rate,
        sum(basket_size)                            as lifetime_items
    from fct
    group by user_id

)

select
    user_id,
    total_orders,
    avg_basket_size,
    avg_days_between_orders,
    avg_reorder_rate,
    lifetime_items,
    case
        when avg_days_between_orders > 20 then 1
        else 0
    end                                             as is_churned,
    case
        when total_orders >= 10
         and avg_reorder_rate >= 0.6  then 'champion'
        when total_orders >= 7
         and avg_reorder_rate >= 0.4  then 'loyal'
        when total_orders >= 4        then 'regular'
        when total_orders >= 2        then 'occasional'
        else                               'new'
    end                                             as customer_tier
from customer_stats