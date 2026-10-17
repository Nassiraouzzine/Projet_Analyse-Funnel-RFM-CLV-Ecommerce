
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select basket_value
from "gold"."main"."mart_funnel"
where basket_value is null



  
  
      
    ) dbt_internal_test