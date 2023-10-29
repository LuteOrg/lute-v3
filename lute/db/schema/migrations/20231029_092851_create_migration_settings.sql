-- Add migration keys to settings
-- Replaces old .env vars.

insert into settings (StKey, StValue) values ('backup_enabled', '-');
insert into settings (StKey, StValue) values ('backup_auto', 'y');
insert into settings (StKey, StValue) values ('backup_warn', 'y');
insert into settings (StKey, StValue) values ('backup_dir', '');
insert into settings (StKey, StValue) values ('backup_count', '5');
