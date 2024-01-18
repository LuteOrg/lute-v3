-- Update statuses for datatables export, to match value required in import.

update statuses set StAbbreviation = 'W' where StID = 99;
update statuses set StAbbreviation = 'I' where StID = 98;
