-- Add migration keys to settings
-- Replaces old .env vars.

insert into settings (StKey, StValue) values ('backup_enabled', '-');
insert into settings (StKey, StValue) values ('backup_auto', '1');
insert into settings (StKey, StValue) values ('backup_warn', '1');
insert into settings (StKey, StValue) values ('backup_dir', '');
insert into settings (StKey, StValue) values ('backup_count', '5');
