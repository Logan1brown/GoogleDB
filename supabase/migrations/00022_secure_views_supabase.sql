-- Enable RLS
alter table show_team enable row level security;
alter table shows enable row level security;
alter table network_list enable row level security;
alter table studio_list enable row level security;
alter table status_types enable row level security;
alter table tmdb_success_metrics enable row level security;

-- Drop existing views
drop view if exists api_show_team cascade;
drop view if exists api_market_analysis cascade;

-- Create secure show team view
create view api_show_team as
select 
    st.id,
    st.show_id,
    st.name,
    st.search_name,
    st.role_type_id,
    st.team_order,
    st.notes,
    st.active,
    st.created_at,
    st.updated_at,
    s.title,
    n.network as network_name
from show_team st
join shows s on st.show_id = s.id
left join network_list n on s.network_id = n.id;

-- Create secure market analysis view
create view api_market_analysis as
select 
    s.tmdb_id,
    s.title,
    n.network as network_name,
    array_agg(distinct st.studio) as studio_names,
    st2.status as status_name,
    s.episode_count,
    tm.seasons as tmdb_seasons,
    tm.total_episodes as tmdb_total_episodes,
    tm.status as tmdb_status,
    tm.last_air_date as tmdb_last_air_date,
    s.date as announced_date
from shows s
left join network_list n on s.network_id = n.id
left join studio_list st on st.id = any (s.studios)
left join status_types st2 on s.status_id = st2.id
left join tmdb_success_metrics tm on s.tmdb_id = tm.tmdb_id
group by s.tmdb_id, s.title, n.network, st2.status, s.episode_count, tm.seasons, tm.total_episodes, tm.status, tm.last_air_date, s.date;

-- Enable RLS on views
alter view api_show_team set (security_invoker = on);
alter view api_market_analysis set (security_invoker = on);

-- Grant access to authenticated users
grant all on api_show_team to authenticated;
grant all on api_market_analysis to authenticated;

-- Grant select to anon users
grant select on api_show_team to anon;
grant select on api_market_analysis to anon;
