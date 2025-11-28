### 1. Check the number of records (Overview)
Get an overview of how much data has been dumped

```sql
-- Check the number of accounts
SELECT COUNT(*) as total_accounts FROM accounts;

-- Check the number of Objekt
SELECT COUNT(*) as total_objekts FROM objekts;

-- Check the number of Unit
SELECT COUNT(*) as total_units FROM units;
```

### 2. Check Data Freshness
Check the records with the latest `last_modified_date` to ensure new data has arrived from Salesforce.
```sql
-- 5 Most Recent Account Changes
SELECT id, name, person_email, account_type__c, last_modified_date 
FROM accounts 
ORDER BY last_modified_date DESC 
LIMIT 5;

-- 5 Most Recent Objekt change
SELECT id, name, address_city, property_manager__c, last_modified_date 
FROM objekts 
ORDER BY last_modified_date DESC 
LIMIT 5;
```
### 3. Check data integrity (Relationship Check)
Since `Unit` is related to `Objekt` via `objekt__c`, and `Objekt` is related to `Account` (the owner) via `owner_id` or `eigentumer__c`. Try Joining to see if the data matches.

```sql
-- Check if Unit points correctly to Object
SELECT 
    u.name AS unit_name,
    u.type_of_unit__c,
    o.name AS building_name,
    o.address_city
FROM units u
JOIN objekts o ON u.objekt__c = o.id
LIMIT 10;
```

```sql
-- Check the Owner of the Object
SELECT 
    o.name AS building_name,
    a.name AS owner_name,
    a.person_email AS owner_email
FROM objekts o
JOIN accounts a ON o.owner_id = a.id
LIMIT 10;
```

### 4. Check important fields are NULL (Data Quality)
Sometimes sync runs but the field is misaligned, check if important columns have data.

```sql
-- Check if any Object is missing an address
SELECT id, name, address_street, address_city 
FROM objekts 
WHERE address_city IS NULL;

-- KCheck if any Account is a Person Account (has personal email)
SELECT id, name, person_email, phone 
FROM accounts 
WHERE person_email IS NOT NULL 
LIMIT 5;
```

### 5. If Reset to test again from the beginning
If want to clear the data to run the command `python main.py full` again to be sure:

```sql

-- Delete in order (Unit deletes first because it depends on Objekt, Objekt deletes first because it depends on Account)
DELETE FROM units;
DELETE FROM objekts;
DELETE FROM accounts;
```