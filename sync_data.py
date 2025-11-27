"""
Salesforce Incremental Sync Script - CORRECTED VERSION
Uses actual Salesforce object names from your org
"""

import asyncio
import asyncpg
from simple_salesforce import Salesforce
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import logging
import os
from dataclasses import dataclass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SyncConfig:
    """Configuration for Salesforce sync"""
    # Salesforce credentials
    sf_username: str
    sf_password: str
    sf_security_token: str
    sf_domain: str = 'login'

    # PostgreSQL credentials
    db_host: str = 'localhost'
    db_port: int = 5432
    db_name: str = 'property_management'
    db_user: str = 'postgres'
    db_password: str = 'your_password'

    # Sync settings
    sync_interval_minutes: int = 5
    batch_size: int = 200


class SalesforceIncrementalSync:
    """Handles incremental sync from Salesforce to PostgreSQL"""

    # Mapping Salesforce objects to PostgreSQL tables
    OBJECT_MAPPING = {
        'Account': 'clients',
        'Objekt__c': 'properties',
        'Hausunit__c': 'units',
        'Beziehung_zur_Einheit__c': 'unit_owners'
    }

    def __init__(self, config: SyncConfig):
        self.config = config
        self.sf: Optional[Salesforce] = None
        self.pool: Optional[asyncpg.Pool] = None

    def connect_salesforce(self):
        """Connect to Salesforce"""
        try:
            self.sf = Salesforce(
                username=self.config.sf_username,
                password=self.config.sf_password,
                security_token=self.config.sf_security_token,
                domain=self.config.sf_domain
            )
            logger.info("✓ Connected to Salesforce")
        except Exception as e:
            logger.error(f"✗ Failed to connect to Salesforce: {e}")
            raise

    async def init_pool(self):
        """Initialize PostgreSQL connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                host=self.config.db_host,
                port=self.config.db_port,
                database=self.config.db_name,
                user=self.config.db_user,
                password=self.config.db_password,
                min_size=5,
                max_size=20
            )
            logger.info("✓ Connected to PostgreSQL")
        except Exception as e:
            logger.error(f"✗ Failed to connect to PostgreSQL: {e}")
            raise

    async def get_last_sync_time(self, object_name: str) -> datetime:
        """Get the last successful sync time for an object"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                "SELECT last_sync_time FROM sync_metadata WHERE object_name = $1",
                object_name
            )
            return result or (datetime.now() - timedelta(days=30))

    async def update_sync_metadata(
            self,
            object_name: str,
            sync_time: datetime,
            record_count: int,
            error: Optional[str] = None
    ):
        """Update sync metadata after sync"""
        async with self.pool.acquire() as conn:
            if error:
                await conn.execute("""
                                   UPDATE sync_metadata
                                   SET total_errors = total_errors + 1,
                                       last_error   = $2,
                                       updated_at   = NOW()
                                   WHERE object_name = $1
                                   """, object_name, error)
            else:
                await conn.execute("""
                                   INSERT INTO sync_metadata (object_name,
                                                              last_sync_time,
                                                              total_records,
                                                              last_successful_sync)
                                   VALUES ($1, $2, $3, $2) ON CONFLICT (object_name) 
                    DO
                                   UPDATE SET
                                       last_sync_time = $2,
                                       total_records = sync_metadata.total_records + $3,
                                       last_successful_sync = $2,
                                       updated_at = NOW()
                                   """, object_name, sync_time, record_count)

    def safe_value(self, val: Any, default=None) -> Any:
        """Safely extract value, return None if null"""
        return val if val not in (None, '', 'null') else default

    async def sync_clients(self) -> int:
        """Sync Account objects (clients)"""
        object_name = 'Account'
        logger.info(f"Syncing {object_name}...")

        try:
            last_sync = await self.get_last_sync_time(object_name)

            # OPTIMIZED: Only fetch fields we actually use
            query = f"""
            SELECT Id, Name, FirstName, LastName, Salutation, MiddleName,
                   PersonEmail, Phone, Mobile_phone__c, PersonMobilePhone, 
                   PersonHomePhone, Other_phone__c, Fax, Website,
                   Email_2__pc, IsPersonAccount, Account_type__c, AccountSource,
                   Contacttype__pc,
                   BillingStreet, BillingCity, BillingPostalCode, BillingState, 
                   BillingCountry, BillingLatitude, BillingLongitude,
                   PersonMailingStreet, PersonMailingCity, PersonMailingPostalCode, 
                   PersonMailingState, PersonMailingCountry, PersonMailingLatitude, 
                   PersonMailingLongitude,
                   ShippingStreet, ShippingCity, ShippingPostalCode, ShippingState, 
                   ShippingCountry,
                   PersonBirthdate, PersonTitle, PersonDepartment,
                   Industry, NumberOfEmployees, Description,
                   Bankverbindung_IBAN__c, Account_Balance__c,
                   IsCustomerPortal, Community_user_ID__pc, Default_community_userID__c,
                   ParentId, MasterRecordId,
                   OwnerId, RecordTypeId, CreatedById, CreatedDate,
                   LastModifiedById, LastModifiedDate, LastActivityDate,
                   SystemModstamp, IsDeleted, IsPriorityRecord, Created_by_auto_flow__c
            FROM Account 
            WHERE LastModifiedDate > {last_sync.isoformat()}
            ORDER BY LastModifiedDate ASC
            LIMIT 2000
            """

            results = self.sf.query_all(query)
            records = results.get('records', [])

            if not records:
                logger.info(f"  No new changes for {object_name}")
                return 0

            logger.info(f"  Found {len(records)} modified records")

            # Upsert to PostgreSQL
            upsert_query = """
                           INSERT INTO clients (sf_id, name, first_name, last_name, salutation, middle_name, \
                                                person_email, phone, mobile_phone, person_mobile_phone, \
                                                person_home_phone, other_phone, fax, website, email_2, \
                                                is_person_account, account_type, account_source, contact_type, \
                                                billing_street, billing_city, billing_postal_code, billing_state, \
                                                billing_country, billing_latitude, billing_longitude, \
                                                person_mailing_street, person_mailing_city, person_mailing_postal_code, \
                                                person_mailing_state, person_mailing_country, person_mailing_latitude, \
                                                person_mailing_longitude, \
                                                shipping_street, shipping_city, shipping_postal_code, shipping_state, \
                                                shipping_country, \
                                                person_birthdate, person_title, person_department, \
                                                industry, number_of_employees, description, \
                                                bank_iban, account_balance, \
                                                is_customer_portal, community_user_id, default_community_user_id, \
                                                parent_id, master_record_id, \
                                                owner_id, record_type_id, created_by_id, created_date, \
                                                last_modified_by_id, last_modified_date, last_activity_date, \
                                                system_modstamp, is_deleted, is_priority_record, created_by_auto_flow) \
                           VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, \
                                   $16, $17, $18, $19, $20, $21, $22, $23, $24, $25, $26, $27, $28, \
                                   $29, $30, $31, $32, $33, $34, $35, $36, $37, $38, $39, $40, $41, \
                                   $42, $43, $44, $45, $46, $47, $48, $49, $50, $51, $52, $53, $54, \
                                   $55, $56, $57, $58, $59) ON CONFLICT (sf_id) DO \
                           UPDATE SET
                               name = EXCLUDED.name, \
                               first_name = EXCLUDED.first_name, \
                               last_name = EXCLUDED.last_name, \
                               person_email = EXCLUDED.person_email, \
                               phone = EXCLUDED.phone, \
                               billing_city = EXCLUDED.billing_city, \
                               billing_street = EXCLUDED.billing_street, \
                               is_person_account = EXCLUDED.is_person_account, \
                               last_modified_date = EXCLUDED.last_modified_date, \
                               is_deleted = EXCLUDED.is_deleted, \
                               synced_at = NOW() \
                           """

            data = []
            for r in records:
                data.append((
                    r['Id'],
                    self.safe_value(r.get('Name')),
                    self.safe_value(r.get('FirstName')),
                    self.safe_value(r.get('LastName')),
                    self.safe_value(r.get('Salutation')),
                    self.safe_value(r.get('MiddleName')),
                    self.safe_value(r.get('PersonEmail')),
                    self.safe_value(r.get('Phone')),
                    self.safe_value(r.get('Mobile_phone__c')),
                    self.safe_value(r.get('PersonMobilePhone')),
                    self.safe_value(r.get('PersonHomePhone')),
                    self.safe_value(r.get('Other_phone__c')),
                    self.safe_value(r.get('Fax')),
                    self.safe_value(r.get('Website')),
                    self.safe_value(r.get('Email_2__pc')),
                    r.get('IsPersonAccount', False),
                    self.safe_value(r.get('Account_type__c')),
                    self.safe_value(r.get('AccountSource')),
                    self.safe_value(r.get('Contacttype__pc')),
                    self.safe_value(r.get('BillingStreet')),
                    self.safe_value(r.get('BillingCity')),
                    self.safe_value(r.get('BillingPostalCode')),
                    self.safe_value(r.get('BillingState')),
                    self.safe_value(r.get('BillingCountry')),
                    self.safe_value(r.get('BillingLatitude')),
                    self.safe_value(r.get('BillingLongitude')),
                    self.safe_value(r.get('PersonMailingStreet')),
                    self.safe_value(r.get('PersonMailingCity')),
                    self.safe_value(r.get('PersonMailingPostalCode')),
                    self.safe_value(r.get('PersonMailingState')),
                    self.safe_value(r.get('PersonMailingCountry')),
                    self.safe_value(r.get('PersonMailingLatitude')),
                    self.safe_value(r.get('PersonMailingLongitude')),
                    self.safe_value(r.get('ShippingStreet')),
                    self.safe_value(r.get('ShippingCity')),
                    self.safe_value(r.get('ShippingPostalCode')),
                    self.safe_value(r.get('ShippingState')),
                    self.safe_value(r.get('ShippingCountry')),
                    self.safe_value(r.get('PersonBirthdate')),
                    self.safe_value(r.get('PersonTitle')),
                    self.safe_value(r.get('PersonDepartment')),
                    self.safe_value(r.get('Industry')),
                    self.safe_value(r.get('NumberOfEmployees')),
                    self.safe_value(r.get('Description')),
                    self.safe_value(r.get('Bankverbindung_IBAN__c')),
                    self.safe_value(r.get('Account_Balance__c')),
                    r.get('IsCustomerPortal', False),
                    self.safe_value(r.get('Community_user_ID__pc')),
                    self.safe_value(r.get('Default_community_userID__c')),
                    self.safe_value(r.get('ParentId')),
                    self.safe_value(r.get('MasterRecordId')),
                    self.safe_value(r.get('OwnerId')),
                    self.safe_value(r.get('RecordTypeId')),
                    self.safe_value(r.get('CreatedById')),
                    self.safe_value(r.get('CreatedDate')),
                    self.safe_value(r.get('LastModifiedById')),
                    self.safe_value(r.get('LastModifiedDate')),
                    self.safe_value(r.get('LastActivityDate')),
                    self.safe_value(r.get('SystemModstamp')),
                    r.get('IsDeleted', False),
                    r.get('IsPriorityRecord', False),
                    r.get('Created_by_auto_flow__c', False)
                ))

            async with self.pool.acquire() as conn:
                await conn.executemany(upsert_query, data)

            await self.update_sync_metadata(object_name, datetime.now(), len(records))
            logger.info(f"  ✓ Synced {len(records)} {object_name} records")
            return len(records)

        except Exception as e:
            error_msg = f"Error syncing {object_name}: {str(e)}"
            logger.error(f"  ✗ {error_msg}")
            await self.update_sync_metadata(object_name, datetime.now(), 0, error_msg)
            return 0

    async def sync_properties(self) -> int:
        """Sync Objekt__c objects"""
        object_name = 'Objekt__c'
        logger.info(f"Syncing {object_name}...")

        try:
            last_sync = await self.get_last_sync_time(object_name)

            # OPTIMIZED: Only essential fields
            query = f"""
            SELECT Id, Name, Objekt_ID__c, Name_system__c, ID_Name__c,
                   Address__Street__s, Address__City__s, Address__PostalCode__s,
                   Address__StateCode__s, Address__CountryCode__s,
                   Address__Latitude__s, Address__Longitude__s,
                   Anzahl_WE__c, Anzahl_Gew__c, Anzahl_Stellplaz__c,
                   Gewerbeeinheiten__c, Wohn_Gewerbeeinheiten__c,
                   Total_houses_and_offices__c, Stellplatze__c, Apartment_unit__c,
                   Difference_WE__c, Difference_GEw__c, Different_stellplatz__c,
                   Type_WEG_MV__c, Verwaltungsstatus__c, Management_level__c,
                   City_group__c, Priority__c,
                   Hausverwaltung__c, Property_manager__c, Management_companyold__c,
                   Objektbuchhalter__c, Eigentumer__c, Hausmeister__c,
                   Hausreinigung__c, Heizung_Sanitar__c, Elektro__c,
                   Messdienstleister__c, Versicherungsmakler__c,
                   Wasserschadenbehebung__c, Winterdienst__c, Schlusseldienst__c,
                   Objekt_emailaddress__c, Owners_emails__c, Tenants_emails__c,
                   In_management_this_year__c, In_management_next_year__c,
                   Letzte_Abrechnung__c, Vertragsende_letzter_SEV_Vertrag__c,
                   Verwaltervertragsende__c, Allgemeine_Hinweise__c,
                   Status_Objektbuchhaltung__c, Checked_and_confirmed__c,
                   Check_today_with_last_SEV_date__c, Check_today_with_last_vertrage_date__c,
                   Picture__c, view_link__c, Impower__c,
                   OwnerId, CreatedById, CreatedDate, LastModifiedById,
                   LastModifiedDate, LastActivityDate, SystemModstamp, IsDeleted
            FROM Objekt__c 
            WHERE LastModifiedDate > {last_sync.isoformat()}
            ORDER BY LastModifiedDate ASC
            LIMIT 2000
            """

            results = self.sf.query_all(query)
            records = results.get('records', [])

            if not records:
                logger.info(f"  No new changes for {object_name}")
                return 0

            logger.info(f"  Found {len(records)} modified records")

            upsert_query = """
                           INSERT INTO properties (sf_id, name, objekt_id, name_system, id_name, \
                                                   address_street, address_city, address_postal_code, address_state, \
                                                   address_country, address_latitude, address_longitude, \
                                                   anzahl_we, anzahl_gew, anzahl_stellplatz, gewerbeeinheiten, \
                                                   wohn_gewerbeeinheiten, total_houses_and_offices, stellplatze, \
                                                   apartment_unit, difference_we, difference_gew, different_stellplatz, \
                                                   type_weg_mo, verwaltungsstatus, management_level, city_group, \
                                                   priority, \
                                                   hausverwaltung, property_manager, management_company_old, \
                                                   objektbuchhalter, \
                                                   eigentumer, hausmeister, hausreinigung, heizung_sanitar, elektro, \
                                                   messdienstleister, versicherungsmakler, wasserschadenbehebung, \
                                                   winterdienst, schlusseldienst, \
                                                   objekt_emailaddress, owners_emails, tenants_emails, \
                                                   in_management_this_year, in_management_next_year, \
                                                   letzte_abrechnung, vertragsende_letzter_sev_vertrag, \
                                                   verwaltervertragsende, \
                                                   allgemeine_hinweise, status_objektbuchhaltung, \
                                                   checked_and_confirmed, check_today_with_last_sev_date, \
                                                   check_today_with_last_vertrage_date, \
                                                   picture_url, view_link, impower_id, \
                                                   owner_id, created_by_id, created_date, last_modified_by_id, \
                                                   last_modified_date, last_activity_date, system_modstamp, is_deleted) \
                           VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, \
                                   $16, $17, $18, $19, $20, $21, $22, $23, $24, $25, $26, $27, $28, \
                                   $29, $30, $31, $32, $33, $34, $35, $36, $37, $38, $39, $40, $41, \
                                   $42, $43, $44, $45, $46, $47, $48, $49, $50, $51, $52, $53, $54, \
                                   $55, $56, $57, $58, $59, $60, $61, $62, $63, $64, $65) ON CONFLICT (sf_id) DO \
                           UPDATE SET
                               name = EXCLUDED.name, \
                               anzahl_we = EXCLUDED.anzahl_we, \
                               anzahl_gew = EXCLUDED.anzahl_gew, \
                               address_city = EXCLUDED.address_city, \
                               last_modified_date = EXCLUDED.last_modified_date, \
                               is_deleted = EXCLUDED.is_deleted, \
                               synced_at = NOW() \
                           """

            data = []
            for r in records:
                data.append((
                    r['Id'],
                    self.safe_value(r.get('Name')),
                    self.safe_value(r.get('Objekt_ID__c')),
                    self.safe_value(r.get('Name_system__c')),
                    self.safe_value(r.get('ID_Name__c')),
                    self.safe_value(r.get('Address__Street__s')),
                    self.safe_value(r.get('Address__City__s')),
                    self.safe_value(r.get('Address__PostalCode__s')),
                    self.safe_value(r.get('Address__StateCode__s')),
                    self.safe_value(r.get('Address__CountryCode__s')),
                    self.safe_value(r.get('Address__Latitude__s')),
                    self.safe_value(r.get('Address__Longitude__s')),
                    self.safe_value(r.get('Anzahl_WE__c')),
                    self.safe_value(r.get('Anzahl_Gew__c')),
                    self.safe_value(r.get('Anzahl_Stellplaz__c')),
                    self.safe_value(r.get('Gewerbeeinheiten__c')),
                    self.safe_value(r.get('Wohn_Gewerbeeinheiten__c')),
                    self.safe_value(r.get('Total_houses_and_offices__c')),
                    self.safe_value(r.get('Stellplatze__c')),
                    self.safe_value(r.get('Apartment_unit__c')),
                    self.safe_value(r.get('Difference_WE__c')),
                    self.safe_value(r.get('Difference_GEw__c')),
                    self.safe_value(r.get('Different_stellplatz__c')),
                    self.safe_value(r.get('Type_WEG_MV__c')),
                    self.safe_value(r.get('Verwaltungsstatus__c')),
                    self.safe_value(r.get('Management_level__c')),
                    self.safe_value(r.get('City_group__c')),
                    self.safe_value(r.get('Priority__c')),
                    self.safe_value(r.get('Hausverwaltung__c')),
                    self.safe_value(r.get('Property_manager__c')),
                    self.safe_value(r.get('Management_companyold__c')),
                    self.safe_value(r.get('Objektbuchhalter__c')),
                    self.safe_value(r.get('Eigentumer__c')),
                    self.safe_value(r.get('Hausmeister__c')),
                    self.safe_value(r.get('Hausreinigung__c')),
                    self.safe_value(r.get('Heizung_Sanitar__c')),
                    self.safe_value(r.get('Elektro__c')),
                    self.safe_value(r.get('Messdienstleister__c')),
                    self.safe_value(r.get('Versicherungsmakler__c')),
                    self.safe_value(r.get('Wasserschadenbehebung__c')),
                    self.safe_value(r.get('Winterdienst__c')),
                    self.safe_value(r.get('Schlusseldienst__c')),
                    self.safe_value(r.get('Objekt_emailaddress__c')),
                    self.safe_value(r.get('Owners_emails__c')),
                    self.safe_value(r.get('Tenants_emails__c')),
                    r.get('In_management_this_year__c', False),
                    r.get('In_management_next_year__c', False),
                    self.safe_value(r.get('Letzte_Abrechnung__c')),
                    self.safe_value(r.get('Vertragsende_letzter_SEV_Vertrag__c')),
                    self.safe_value(r.get('Verwaltervertragsende__c')),
                    self.safe_value(r.get('Allgemeine_Hinweise__c')),
                    self.safe_value(r.get('Status_Objektbuchhaltung__c')),
                    r.get('Checked_and_confirmed__c', False),
                    r.get('Check_today_with_last_SEV_date__c', False),
                    r.get('Check_today_with_last_vertrage_date__c', False),
                    self.safe_value(r.get('Picture__c')),
                    self.safe_value(r.get('view_link__c')),
                    self.safe_value(r.get('Impower__c')),
                    self.safe_value(r.get('OwnerId')),
                    self.safe_value(r.get('CreatedById')),
                    self.safe_value(r.get('CreatedDate')),
                    self.safe_value(r.get('LastModifiedById')),
                    self.safe_value(r.get('LastModifiedDate')),
                    self.safe_value(r.get('LastActivityDate')),
                    self.safe_value(r.get('SystemModstamp')),
                    r.get('IsDeleted', False)
                ))

            async with self.pool.acquire() as conn:
                await conn.executemany(upsert_query, data)

            await self.update_sync_metadata(object_name, datetime.now(), len(records))
            logger.info(f"  ✓ Synced {len(records)} {object_name} records")
            return len(records)

        except Exception as e:
            error_msg = f"Error syncing {object_name}: {str(e)}"
            logger.error(f"  ✗ {error_msg}")
            await self.update_sync_metadata(object_name, datetime.now(), 0, error_msg)
            return 0

    async def sync_units(self) -> int:
        """Sync Hausunit__c objects"""
        object_name = 'Hausunit__c'
        logger.info(f"Syncing {object_name}...")

        try:
            last_sync = await self.get_last_sync_time(object_name)

            query = f"""
            SELECT Id, Name, Description__c, Objekt__c, Objekt_text__c,
                   Type_of_unit__c, Bauart__c, Wohnflache__c, Heizflache__c,
                   Count_active_SEV_contracts__c, Count_vertrage__c,
                   Last_vertrag_start_date__c, Last_vertrage_end_date__c,
                   Owner_note__c, AccountingID__c, Impower_Unit_ID__c, Trigger__c,
                   CreatedById, CreatedDate, LastModifiedById, LastModifiedDate,
                   LastActivityDate, SystemModstamp, IsDeleted
            FROM Hausunit__c 
            WHERE LastModifiedDate > {last_sync.isoformat()}
            ORDER BY LastModifiedDate ASC
            LIMIT 2000
            """

            results = self.sf.query_all(query)
            records = results.get('records', [])

            if not records:
                logger.info(f"  No new changes for {object_name}")
                return 0

            logger.info(f"  Found {len(records)} modified records")

            upsert_query = """
                           INSERT INTO units (sf_id, name, description, objekt_id, objekt_text, type_of_unit, \
                                              bauart, wohnflache, heizflache, count_active_sev_contracts, \
                                              count_vertrage, last_vertrag_start_date, last_vertrage_end_date, \
                                              owner_note, accounting_id, impower_unit_id, trigger_field, \
                                              created_by_id, created_date, last_modified_by_id, last_modified_date, \
                                              last_activity_date, system_modstamp, is_deleted) \
                           VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, \
                                   $16, $17, $18, $19, $20, $21, $22, $23, $24) ON CONFLICT (sf_id) DO \
                           UPDATE SET
                               name = EXCLUDED.name, \
                               description = EXCLUDED.description, \
                               type_of_unit = EXCLUDED.type_of_unit, \
                               wohnflache = EXCLUDED.wohnflache, \
                               last_modified_date = EXCLUDED.last_modified_date, \
                               is_deleted = EXCLUDED.is_deleted, \
                               synced_at = NOW() \
                           """

            data = []
            for r in records:
                data.append((
                    r['Id'],
                    self.safe_value(r.get('Name')),
                    self.safe_value(r.get('Description__c')),
                    self.safe_value(r.get('Objekt__c')),
                    self.safe_value(r.get('Objekt_text__c')),
                    self.safe_value(r.get('Type_of_unit__c')),
                    self.safe_value(r.get('Bauart__c')),
                    self.safe_value(r.get('Wohnflache__c')),
                    self.safe_value(r.get('Heizflache__c')),
                    self.safe_value(r.get('Count_active_SEV_contracts__c')),
                    self.safe_value(r.get('Count_vertrage__c')),
                    self.safe_value(r.get('Last_vertrag_start_date__c')),
                    self.safe_value(r.get('Last_vertrage_end_date__c')),
                    self.safe_value(r.get('Owner_note__c')),
                    self.safe_value(r.get('AccountingID__c')),
                    self.safe_value(r.get('Impower_Unit_ID__c')),
                    self.safe_value(r.get('Trigger__c')),
                    self.safe_value(r.get('CreatedById')),
                    self.safe_value(r.get('CreatedDate')),
                    self.safe_value(r.get('LastModifiedById')),
                    self.safe_value(r.get('LastModifiedDate')),
                    self.safe_value(r.get('LastActivityDate')),
                    self.safe_value(r.get('SystemModstamp')),
                    r.get('IsDeleted', False)
                ))

            async with self.pool.acquire() as conn:
                await conn.executemany(upsert_query, data)

            await self.update_sync_metadata(object_name, datetime.now(), len(records))
            logger.info(f"  ✓ Synced {len(records)} {object_name} records")
            return len(records)

        except Exception as e:
            error_msg = f"Error syncing {object_name}: {str(e)}"
            logger.error(f"  ✗ {error_msg}")
            await self.update_sync_metadata(object_name, datetime.now(), 0, error_msg)
            return 0

    async def sync_unit_owners(self) -> int:
        """Sync Beziehung_zur_Einheit__c objects"""
        object_name = 'Beziehung_zur_Einheit__c'
        logger.info(f"Syncing {object_name}...")

        try:
            last_sync = await self.get_last_sync_time(object_name)

            query = f"""
            SELECT Id, Name, Owner__c, Unit__c, Parent_Objekt__c,
                   Objekt_name__c, Haus_unit_description__c,
                   Start_date__c, End_date__c, Active__c,
                   OwnerId, CreatedById, CreatedDate, LastModifiedById,
                   LastModifiedDate, LastActivityDate, SystemModstamp, IsDeleted
            FROM Beziehung_zur_Einheit__c 
            WHERE LastModifiedDate > {last_sync.isoformat()}
            ORDER BY LastModifiedDate ASC
            LIMIT 2000
            """

            results = self.sf.query_all(query)
            records = results.get('records', [])

            if not records:
                logger.info(f"  No new changes for {object_name}")
                return 0

            logger.info(f"  Found {len(records)} modified records")

            upsert_query = """
                           INSERT INTO unit_owners (sf_id, name, owner_id, unit_id, parent_objekt_id, objekt_name, \
                                                    haus_unit_description, start_date, end_date, active, sf_owner_id, \
                                                    created_by_id, created_date, last_modified_by_id, \
                                                    last_modified_date, \
                                                    last_activity_date, system_modstamp, is_deleted) \
                           VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, \
                                   $16, $17, $18) ON CONFLICT (sf_id) DO \
                           UPDATE SET
                               owner_id = EXCLUDED.owner_id, \
                               unit_id = EXCLUDED.unit_id, \
                               start_date = EXCLUDED.start_date, \
                               end_date = EXCLUDED.end_date, \
                               active = EXCLUDED.active, \
                               last_modified_date = EXCLUDED.last_modified_date, \
                               is_deleted = EXCLUDED.is_deleted, \
                               synced_at = NOW() \
                           """

            data = []
            for r in records:
                data.append((
                    r['Id'],
                    self.safe_value(r.get('Name')),
                    self.safe_value(r.get('Owner__c')),
                    self.safe_value(r.get('Unit__c')),
                    self.safe_value(r.get('Parent_Objekt__c')),
                    self.safe_value(r.get('Objekt_name__c')),
                    self.safe_value(r.get('Haus_unit_description__c')),
                    self.safe_value(r.get('Start_date__c')),
                    self.safe_value(r.get('End_date__c')),
                    r.get('Active__c', False),
                    self.safe_value(r.get('OwnerId')),
                    self.safe_value(r.get('CreatedById')),
                    self.safe_value(r.get('CreatedDate')),
                    self.safe_value(r.get('LastModifiedById')),
                    self.safe_value(r.get('LastModifiedDate')),
                    self.safe_value(r.get('LastActivityDate')),
                    self.safe_value(r.get('SystemModstamp')),
                    r.get('IsDeleted', False)
                ))

            async with self.pool.acquire() as conn:
                await conn.executemany(upsert_query, data)

            await self.update_sync_metadata(object_name, datetime.now(), len(records))
            logger.info(f"  ✓ Synced {len(records)} {object_name} records")
            return len(records)

        except Exception as e:
            error_msg = f"Error syncing {object_name}: {str(e)}"
            logger.error(f"  ✗ {error_msg}")
            await self.update_sync_metadata(object_name, datetime.now(), 0, error_msg)
            return 0

    async def sync_all(self):
        """Sync all objects in correct order"""
        logger.info("=" * 80)
        logger.info(f"Starting incremental sync at {datetime.now()}")
        logger.info("=" * 80)

        start_time = datetime.now()

        # Sync in order: clients -> properties -> units -> ownership
        total_clients = await self.sync_clients()
        total_properties = await self.sync_properties()
        total_units = await self.sync_units()
        total_owners = await self.sync_unit_owners()

        elapsed = (datetime.now() - start_time).total_seconds()
        total_records = total_clients + total_properties + total_units + total_owners

        logger.info("=" * 80)
        logger.info("Sync Summary:")
        logger.info(f"  • Clients (Account): {total_clients}")
        logger.info(f"  • Properties (Objekt__c): {total_properties}")
        logger.info(f"  • Units (Hausunit__c): {total_units}")
        logger.info(f"  • Ownership (Beziehung_zur_Einheit__c): {total_owners}")
        logger.info(f"  • Total: {total_records} records")
        logger.info(f"  • Duration: {elapsed:.2f}s")
        logger.info("=" * 80)

    async def run_continuous(self):
        """Run sync continuously at specified interval"""
        logger.info(f"Starting continuous sync (every {self.config.sync_interval_minutes} minutes)")

        while True:
            try:
                await self.sync_all()
                logger.info(f"Next sync in {self.config.sync_interval_minutes} minutes...")
                await asyncio.sleep(self.config.sync_interval_minutes * 60)
            except KeyboardInterrupt:
                logger.info("Sync interrupted by user")
                break
            except Exception as e:
                logger.error(f"Sync error: {e}", exc_info=True)
                logger.info("Waiting 1 minute before retry...")
                await asyncio.sleep(60)

    async def close(self):
        """Close connections"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connections closed")


async def main():
    """Main execution"""

    config = SyncConfig(
        # Salesforce credentials
        sf_username=os.getenv('SF_USERNAME', 'your_username@example.com'),
        sf_password=os.getenv('SF_PASSWORD', 'your_password'),
        sf_security_token=os.getenv('SF_SECURITY_TOKEN', 'your_token'),

        # PostgreSQL credentials
        db_host=os.getenv('DB_HOST', 'localhost'),
        db_port=int(os.getenv('DB_PORT', '5432')),
        db_name=os.getenv('DB_NAME', 'property_management'),
        db_user=os.getenv('DB_USER', 'postgres'),
        db_password=os.getenv('DB_PASSWORD', 'your_password'),

        # Sync interval in minutes
        sync_interval_minutes=int(os.getenv('SYNC_INTERVAL', '5'))
    )

    syncer = SalesforceIncrementalSync(config)

    try:
        syncer.connect_salesforce()
        await syncer.init_pool()

        run_mode = os.getenv('RUN_MODE', 'continuous')

        if run_mode == 'once':
            await syncer.sync_all()
        else:
            await syncer.run_continuous()

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        await syncer.close()


if __name__ == "__main__":
    asyncio.run(main())