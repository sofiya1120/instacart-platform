with source as (

    select * from {{ source('raw', 'raw_order_products') }}

)

select
    order_id::integer               as order_id,
    product_id::integer             as product_id,
    add_to_cart_order::integer      as cart_position,
    reordered::integer              as is_reordered
from source
where order_id   is not null
  and product_id is not null