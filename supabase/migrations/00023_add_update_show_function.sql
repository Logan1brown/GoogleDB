-- Add update_show function for modifying show records
-- This function allows updating all fields of a show record while maintaining audit logs

begin;

create or replace function update_show(
  p_id bigint,
  p_title text,
  p_network_id bigint,
  p_genre_id bigint,
  p_subgenres bigint[],
  p_source_type_id bigint,
  p_order_type_id bigint,
  p_status_id bigint,
  p_episode_count integer,
  p_description text,
  p_studios bigint[]
) returns json as $$
begin
  -- Update the show
  update shows
  set
    title = p_title,
    network_id = p_network_id,
    genre_id = p_genre_id,
    subgenres = p_subgenres,
    source_type_id = p_source_type_id,
    order_type_id = p_order_type_id,
    status_id = p_status_id,
    episode_count = p_episode_count,
    description = p_description,
    studios = p_studios,
    updated_at = now()
  where id = p_id;

  -- Return the updated row
  return row_to_json(
    (select r from (
      select * from shows where id = p_id
    ) r)
  );
end;
$$ language plpgsql;

-- Grant execute permission to authenticated users
grant execute on function update_show to authenticated;

commit;
