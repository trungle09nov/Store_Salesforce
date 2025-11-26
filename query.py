import asyncio
import asyncpg
from simple_salesforce import Salesforce
from datetime import datetime, timedelta
import os
from typing import List, Dict

class SalesforceSyncer:
    def __init__(self):
        self.sf = Salesforce(
            username=os.getenv('SF_USERNAME'),
            password=os.getenv('SF_PASSWORD'),
            security_token=os.getenv('SF_SECURITY_TOKEN')
        )
        self.pool = None

    async def init_pool(self):
        self.pool = await asyncpg.create_pool(
            host='localhost',
            database='property_db',
            user='postgres',
            password='your_password',
            min_size=5,
            max_size=20
        )

    async def get_last_sync_time(self, object_name: str) -> datetime:
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT last_sync_time FROM sync_metadata WHERE object_name = $1",
                object_name
            )
            return result or datetime(2020, 1, 1)

    async def update_sync_time(self, object_name: str, sync_time: datetime, count: int):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO sync_metadata (object_name, last_sync_time, total_records)
                VALUES ($1, $2, $3)
                ON CONFLICT (object_name) 
                DO UPDATE SET 
                    last_sync_time = $2,
                    total_records = $3
            """, object_name, sync_time, count)

    async def sync_clients(self):
        """Sync Accounts (Owners & Tenants)"""
        last_sync = await self.get_last_sync_time('Account')

        # Adjust based on your Salesforce field names
        query = f"""
        SELECT Id, Name, Type, PersonEmail, Phone, 
               BillingStreet, BillingCity, LastModifiedDate
        FROM Account 
        WHERE LastModifiedDate > {last_sync.isoformat()}
        ORDER BY LastModifiedDate ASC
        """

        results = self.sf.query_all(query)
        records = results['records']

        if not records:
            print(f"No new clients to sync")
            return

        async with self.pool.acquire() as conn:
            await conn.executemany("""
                INSERT INTO clients (sf_id, name, type, email, phone, last_modified)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (sf_id) 
                DO UPDATE SET 
                    name = EXCLUDED.name,
                    type = EXCLUDED.type,
                    email = EXCLUDED.email,
                    phone = EXCLUDED.phone,
                    last_modified = EXCLUDED.last_modified
            """, [
                (
                    r['Id'],
                    r['Name'],
                    r.get('Type'),
                    r.get('PersonEmail'),
                    r.get('Phone'),
                    r['LastModifiedDate']
                ) for r in records
            ])

        await self.update_sync_time('Account', datetime.now(), len(records))
        print(f"Synced {len(records)} clients")

    async def sync_properties(self):
        """Sync Property__c custom object"""
        last_sync = await self.get_last_sync_time('Property__c')

        query = f"""
        SELECT Id, Name, Address__c, City__c, Country__c, 
               Total_Units__c, LastModifiedDate
        FROM Property__c 
        WHERE LastModifiedDate > {last_sync.isoformat()}
        """

        results = self.sf.query_all(query)
        records = results['records']

        if not records:
            print("No new properties to sync")
            return

        async with self.pool.acquire() as conn:
            await conn.executemany("""
                INSERT INTO properties (sf_id, name, address, city, country, total_units, last_modified)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (sf_id) 
                DO UPDATE SET 
                    name = EXCLUDED.name,
                    address = EXCLUDED.address,
                    city = EXCLUDED.city,
                    country = EXCLUDED.country,
                    total_units = EXCLUDED.total_units,
                    last_modified = EXCLUDED.last_modified
            """, [
                (
                    r['Id'],
                    r['Name'],
                    r.get('Address__c'),
                    r.get('City__c'),
                    r.get('Country__c'),
                    r.get('Total_Units__c'),
                    r['LastModifiedDate']
                ) for r in records
            ])

        await self.update_sync_time('Property__c', datetime.now(), len(records))
        print(f"Synced {len(records)} properties")

    async def sync_units(self):
        """Sync Unit__c custom object"""
        last_sync = await self.get_last_sync_time('Unit__c')

        query = f"""
        SELECT Id, Name, Property__c, Unit_Number__c, Floor__c,
               Square_Meters__c, Bedrooms__c, Status__c, 
               Rent_Amount__c, LastModifiedDate
        FROM Unit__c 
        WHERE LastModifiedDate > {last_sync.isoformat()}
        """

        results = self.sf.query_all(query)
        records = results['records']

        if not records:
            print("No new units to sync")
            return

        # Get property mapping
        async with self.pool.acquire() as conn:
            sf_to_db_properties = dict(await conn.fetch(
                "SELECT sf_id, id FROM properties"
            ))

            data_to_insert = []
            for r in records:
                property_db_id = sf_to_db_properties.get(r.get('Property__c'))
                if property_db_id:
                    data_to_insert.append((
                        r['Id'],
                        property_db_id,
                        r.get('Unit_Number__c'),
                        r.get('Floor__c'),
                        r.get('Square_Meters__c'),
                        r.get('Bedrooms__c'),
                        r.get('Status__c'),
                        r.get('Rent_Amount__c'),
                        r['LastModifiedDate']
                    ))

            await conn.executemany("""
                INSERT INTO units (sf_id, property_id, unit_number, floor, 
                                 square_meters, bedrooms, status, rent_amount, last_modified)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (sf_id) 
                DO UPDATE SET 
                    property_id = EXCLUDED.property_id,
                    unit_number = EXCLUDED.unit_number,
                    floor = EXCLUDED.floor,
                    square_meters = EXCLUDED.square_meters,
                    bedrooms = EXCLUDED.bedrooms,
                    status = EXCLUDED.status,
                    rent_amount = EXCLUDED.rent_amount,
                    last_modified = EXCLUDED.last_modified
            """, data_to_insert)

        await self.update_sync_time('Unit__c', datetime.now(), len(records))
        print(f"Synced {len(records)} units")

    async def sync_ownership(self):
        """Sync Unit_Owner__c junction object"""
        last_sync = await self.get_last_sync_time('Unit_Owner__c')

        query = f"""
        SELECT Id, Unit__c, Owner__c, Ownership_Percentage__c,
               Start_Date__c, End_Date__c, LastModifiedDate
        FROM Unit_Owner__c 
        WHERE LastModifiedDate > {last_sync.isoformat()}
        """

        results = self.sf.query_all(query)
        records = results['records']

        if not records:
            print("No new ownership records to sync")
            return

        async with self.pool.acquire() as conn:
            # Get mappings
            unit_map = dict(await conn.fetch("SELECT sf_id, id FROM units"))
            client_map = dict(await conn.fetch("SELECT sf_id, id FROM clients"))

            data_to_insert = []
            for r in records:
                unit_id = unit_map.get(r.get('Unit__c'))
                client_id = client_map.get(r.get('Owner__c'))

                if unit_id and client_id:
                    data_to_insert.append((
                        r['Id'],
                        unit_id,
                        client_id,
                        r.get('Ownership_Percentage__c'),
                        r.get('Start_Date__c'),
                        r.get('End_Date__c'),
                        r['LastModifiedDate']
                    ))

            await conn.executemany("""
                INSERT INTO unit_owners (sf_id, unit_id, client_id, ownership_percentage,
                                        start_date, end_date, last_modified)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (sf_id) 
                DO UPDATE SET 
                    unit_id = EXCLUDED.unit_id,
                    client_id = EXCLUDED.client_id,
                    ownership_percentage = EXCLUDED.ownership_percentage,
                    start_date = EXCLUDED.start_date,
                    end_date = EXCLUDED.end_date,
                    last_modified = EXCLUDED.last_modified
            """, data_to_insert)

        await self.update_sync_time('Unit_Owner__c', datetime.now(), len(records))
        print(f"Synced {len(records)} ownership records")

    async def sync_all(self):
        """Run full sync in correct order (respecting foreign keys)"""
        print(f"Starting sync at {datetime.now()}")

        # Order matters: parent objects first
        await self.sync_clients()
        await self.sync_properties()
        await self.sync_units()
        await self.sync_ownership()
        # Add sync_tenancy() similarly

        print(f"Sync completed at {datetime.now()}")

    async def close(self):
        if self.pool:
            await self.pool.close()

# Main execution
async def main():
    syncer = SalesforceSyncer()
    await syncer.init_pool()

    try:
        # Run once
        await syncer.sync_all()

        # Or run in loop every N minutes
        # while True:
        #     await syncer.sync_all()
        #     await asyncio.sleep(300)  # 5 minutes
    finally:
        await syncer.close()

if __name__ == "__main__":
    asyncio.run(main())