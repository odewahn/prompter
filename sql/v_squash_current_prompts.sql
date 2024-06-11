SELECT
  b.tag as tag,
  b.parent_id as parent_id,
  group_concat(pr.response,?) as block
FROM
  prompt_responses pr
  join blocks b on b.id = pr.block_id 
  left join current_group cg on cg.id = b.group_id
group by
  tag,
	parent_id
order by
  tag