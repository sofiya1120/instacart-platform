with source as (

    select * from {{ source('raw', 'raw_orders') }}

),

cleaned as (

    select
        order_id::integer                       as order_id,
        user_id::integer                        as user_id,
        eval_set                                as dataset_split,
        order_number::integer                   as order_number,
        order_dow::integer                      as order_day_of_week,
        case order_dow::integer
            when 0 then 'Sunday'
            when 1 then 'Monday'
            when 2 then 'Tuesday'
            when 3 then 'Wednesday'
            when 4 then 'Thursday'
            when 5 then 'Friday'
            when 6 then 'Saturday'
        end                                     as order_day_name,
        order_hour_of_day::integer              as order_hour,
        case
            when days_since_prior_order is null
            then 0
            else days_since_prior_order::numeric
        end                                     as days_since_prior_order
    from source
    where order_id is not null
      and user_id is not null

)

select * from cleaned