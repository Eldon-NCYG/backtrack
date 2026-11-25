-- Singular test: returns rows that should not exist. dbt fails the test if any come back.
select *
from {{ ref('stg_plays') }}
where played_at > current_timestamp
