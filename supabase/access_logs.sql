-- IPアドレスを含むアクセス状況を保存するテーブル（保存期間: 最大90日）
create table if not exists public.access_logs (
    id uuid primary key default gen_random_uuid(),
    visitor_id text not null,
    player_name text,
    device_info jsonb not null default '{}'::jsonb,
    ip_address inet not null,
    current_page text not null default 'title',
    first_seen timestamptz not null default now(),
    last_seen timestamptz not null default now(),
    expires_at timestamptz not null default (now() + interval '90 days')
);

create unique index if not exists access_logs_visitor_id_key
    on public.access_logs(visitor_id);
create index if not exists access_logs_last_seen_idx
    on public.access_logs(last_seen);

revoke all on public.access_logs from anon, authenticated;
revoke all on public.access_logs from public;

grant usage on schema public to service_role;
grant select, insert, update, delete on table public.access_logs to service_role;

grant usage on schema public to service_role;
grant select, insert, update, delete on table public.rankings to service_role;

alter table public.access_logs
    add column if not exists current_page text not null default 'title';

alter table public.rankings
    add column if not exists visitor_id text;
create index if not exists rankings_visitor_id_idx
    on public.rankings(visitor_id);
