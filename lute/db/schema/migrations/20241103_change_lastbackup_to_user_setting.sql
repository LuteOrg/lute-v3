-- Change lastbackup to from system to user key.

update settings set StKeyType = 'user' where StKey = 'lastbackup';
