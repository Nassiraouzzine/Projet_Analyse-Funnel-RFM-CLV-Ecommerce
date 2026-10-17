
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select payment_mode_proxy
from "gold"."main"."dim_payment"
where payment_mode_proxy is null



  
  
      
    ) dbt_internal_test