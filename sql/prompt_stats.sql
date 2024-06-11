select 
   sum(token_count) approximate_tokens_processed,
   sum(elapsed_time_in_seconds) elapsed_seconds
from 
   prompt_responses pr
   join blocks b on pr.block_id = b.id