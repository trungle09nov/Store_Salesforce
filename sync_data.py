"""
Salesforce to PostgreSQL Sync
Just fetch data from SF API and update to PostgreSQL
"""

import os
import requests
import psycopg2
from psycopg2.extras import execute_batch
import logging
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SalesforceAPI:
    """Salesforce API client"""

    def __init__(self, instance_url: str, api_version: str, access_token: str):
        self.instance_url = instance_url
        self.api_version = api_version
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

    def query(self, soql: str) -> list:
        """Execute SOQL query and return all records"""
        # Clean query string: remove newlines and extra spaces
        clean_soql = " ".join(soql.split())

        url = f"{self.instance_url}/services/data/{self.api_version}/query/"
        params = {'q': clean_soql}

        all_records = []

        try:
            # Initial request
            response = requests.get(url, headers=self.headers, params=params)

            # Error handling for bad queries
            if response.status_code == 400:
                logger.error(f"Bad Request (400). Query sent: {clean_soql}")
                logger.error(f"Response: {response.text}")

            response.raise_for_status()
            data = response.json()

            # Get records
            records = data.get('records', [])
            all_records.extend(records)

            # Handle pagination
            while not data.get('done', True):
                next_url = data.get('nextRecordsUrl')
                if not next_url:
                    break

                logger.info(f"Fetching next batch... (total: {len(all_records)})")
                response = requests.get(f"{self.instance_url}{next_url}", headers=self.headers)
                response.raise_for_status()
                data = response.json()
                all_records.extend(data.get('records', []))

            logger.info(f"Fetched {len(all_records)} records")
            return all_records

        except requests.exceptions.RequestException as e:
            logger.error(f"Query failed: {e}")
            raise


class PostgresDB:
    """PostgreSQL client"""

    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.conn_params = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
        self.conn = None

    def connect(self):
        """Connect to database"""
        self.conn = psycopg2.connect(**self.conn_params)
        self.conn.autocommit = False
        logger.info(f"Connected to PostgreSQL: {self.conn_params['database']}")

    def close(self):
        """Close connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def upsert_records(self, table: str, records: list, upsert_sql: str):
        """Insert or update records"""
        if not records:
            logger.warning(f"No records to sync for {table}")
            return

        logger.info(f"Upserting {len(records)} records to {table}...")

        # Clean records (remove Salesforce metadata)
        clean_records = []
        for record in records:
            # Remove 'attributes' which contains URL and Type info
            clean = {k: v for k, v in record.items() if not k.startswith('attributes')}
            clean_records.append(clean)

        try:
            cursor = self.conn.cursor()
            execute_batch(cursor, upsert_sql, clean_records, page_size=100)
            self.conn.commit()
            logger.info(f"✓ Successfully synced {len(records)} records to {table}")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"✗ Failed to sync {table}: {e}")
            # Print first record to help debug keys
            if clean_records:
                logger.error(f"Sample record keys: {clean_records[0].keys()}")
            raise


class SalesforceSync:
    """Main sync orchestrator"""

    # SOQL Queries - STRICTLY MATCHING USER DUMP
    QUERIES = {
        'account': """
            SELECT 
                Id, Name, Salutation, FirstName, LastName, MiddleName, Suffix,
                OwnerId, RecordTypeId, ParentId,
                Account_Balance__c,
                PersonEmail, PersonMobilePhone, PersonHomePhone, 
                PersonAssistantPhone,
                Phone, Email__c, Email_2__pc, Email_2__c, Mobile_phone__c,
                Other_mobile_phone__pc, Other_phone__c, Fax, Website,
                BillingStreet, BillingCity, BillingState, BillingPostalCode, BillingCountry,
                BillingLatitude, BillingLongitude,
                ShippingStreet, ShippingCity, ShippingState, ShippingPostalCode, ShippingCountry,
                ShippingLatitude, ShippingLongitude,
                PersonMailingStreet, PersonMailingCity, PersonMailingState,
                PersonMailingPostalCode, PersonMailingCountry, PersonMailingLatitude, PersonMailingLongitude,
                PersonOtherPhone,
                AccountSource, Industry,
                Contact_import_sourc__pc, Account_type__c, Contacttype__pc,
                PersonBirthdate, PersonTitle, PersonDepartment,
                IsCustomerPortal, NumberOfEmployees, SicDesc,
                Bankverbindung_IBAN__c, Freistellungs_bescheinigung__c,
                Inside_ID__pc, Community_user_ID__pc, Default_community_userID__c,
                Community_user_calculation__c, Created_by_auto_flow__c,
                PersonIndividualId, PersonReportsToId,
                FlowToolKit__Latest_Form_Submission__c, FlowToolKit__Latest_Form_Submission__pc,
                Novumstate_campaign__pc,
                Description, Jigsaw, SourceSystemIdentifier,
                CreatedById, CreatedDate, LastModifiedById, LastModifiedDate,
                PersonLastCURequestDate, PersonLastCUUpdateDate
            FROM Account
            WHERE IsDeleted = false
        """,

        'objekt': """
            SELECT 
                Id, Name, Objekt_ID__c,
                Address__Street__s, Address__City__s, Address__StateCode__s, 
                Address__PostalCode__s, Address__CountryCode__s, 
                Address__Latitude__s, Address__Longitude__s,
                Anzahl_WE__c, Anzahl_Gew__c, Anzahl_Stellplaz__c, Number_of_other_unit_types__c,
                Apartment_unit__c, Gewerbeeinheiten__c, Stellplatze__c,
                In_management_this_year__c, In_management_next_year__c,
                Vertragsende_letzter_SEV_Vertrag__c, Verwaltervertragsende__c,
                Difference_WE__c, Difference_GEw__c, Different_stellplatz__c,
                Total_houses_and_offices__c, Wohn_Gewerbeeinheiten__c,
                Check_today_with_last_SEV_date__c, Check_today_with_last_vertrage_date__c,
                City_group__c, Management_level__c, Property_manager__c, Verwaltungsstatus__c,
                ID_Name__c, view_link__c,
                Eigentumer__c, Hausmeister__c, Hausreinigung__c, Elektro__c, 
                Heizung_Sanitar__c, Messdienstleister__c, Schlusseldienst__c, 
                Versicherungsmakler__c, Wasserschadenbehebung__c, Winterdienst__c, 
                Management_companyold__c,
                Hausverwaltung__c, Objektbuchhalter__c, OwnerId,
                Contract_origin_objekt__c, Name_system__c, Priority__c, Type_WEG_MV__c,
                Objekt_emailaddress__c, Owners_emails__c, Tenants_emails__c,
                Picture__c, Letzte_Abrechnung__c, Allgemeine_Hinweise__c, 
                Status_Objektbuchhaltung__c, Checked_and_confirmed__c,
                Impower__c,
                CreatedById, CreatedDate, LastModifiedById, LastModifiedDate
            FROM Objekt__c
            WHERE IsDeleted = false
        """,

        'unit': """
            SELECT 
                Id, Name, Description__c, Objekt__c,
                Type_of_unit__c, Bauart__c, Wohnflache__c, Heizflache__c,
                AccountingID__c, Impower_Unit_ID__c,
                Count_active_SEV_contracts__c, Count_vertrage__c,
                Last_vertrag_start_date__c, Last_vertrage_end_date__c,
                Objekt_text__c, Owner_note__c, Trigger__c,
                CreatedById, CreatedDate, LastModifiedById, LastModifiedDate
            FROM Hausunit__c
            WHERE IsDeleted = false
        """
    }

    # Upsert SQL - Matched strictly to the simplified queries above
    UPSERT_SQL = {
        'account': """
            INSERT INTO accounts (
                id, name, salutation, first_name, last_name, middle_name, suffix,
                owner_id, record_type_id, parent_id,
                account_balance,
                person_email, person_mobile_phone, person_home_phone,
                person_assistant_phone,
                phone, email__c, email_2__pc, email_2__c, mobile_phone__c,
                other_mobile_phone__pc, other_phone__c, fax, website,
                billing_street, billing_city, billing_state, billing_postal_code, billing_country,
                billing_latitude, billing_longitude,
                shipping_street, shipping_city, shipping_state, shipping_postal_code, shipping_country,
                shipping_latitude, shipping_longitude,
                person_mailing_street, person_mailing_city, person_mailing_state,
                person_mailing_postal_code, person_mailing_country,
                person_mailing_latitude, person_mailing_longitude,
                person_other_phone,
                account_source, industry,
                contact_import_sourc__pc,
                account_type__c, contacttype__pc,
                person_birthdate, person_title, person_department,
                is_customer_portal, number_of_employees, sic_desc,
                bankverbindung_iban__c, freistellungs_bescheinigung__c,
                inside_id__pc, community_user_id__pc, default_community_userid__c,
                community_user_calculation__c, created_by_auto_flow__c,
                person_individual_id, person_reports_to_id,
                flowtoolkit__latest_form_submission__c, flowtoolkit__latest_form_submission__pc,
                novumstate_campaign__pc,
                description, jigsaw, source_system_identifier,
                created_by_id, created_date, last_modified_by_id, last_modified_date,
                person_last_cu_request_date, person_last_cu_update_date
            ) VALUES (
                %(Id)s, %(Name)s, %(Salutation)s, %(FirstName)s, %(LastName)s, %(MiddleName)s, %(Suffix)s,
                %(OwnerId)s, %(RecordTypeId)s, %(ParentId)s,
                %(Account_Balance__c)s,
                %(PersonEmail)s, %(PersonMobilePhone)s, %(PersonHomePhone)s,
                %(PersonAssistantPhone)s,
                %(Phone)s, %(Email__c)s, %(Email_2__pc)s, %(Email_2__c)s, %(Mobile_phone__c)s,
                %(Other_mobile_phone__pc)s, %(Other_phone__c)s, %(Fax)s, %(Website)s,
                %(BillingStreet)s, %(BillingCity)s, %(BillingState)s, %(BillingPostalCode)s, %(BillingCountry)s,
                %(BillingLatitude)s, %(BillingLongitude)s,
                %(ShippingStreet)s, %(ShippingCity)s, %(ShippingState)s, %(ShippingPostalCode)s, %(ShippingCountry)s,
                %(ShippingLatitude)s, %(ShippingLongitude)s,
                %(PersonMailingStreet)s, %(PersonMailingCity)s, %(PersonMailingState)s,
                %(PersonMailingPostalCode)s, %(PersonMailingCountry)s,
                %(PersonMailingLatitude)s, %(PersonMailingLongitude)s,
                %(PersonOtherPhone)s,
                %(AccountSource)s, %(Industry)s,
                %(Contact_import_sourc__pc)s,
                %(Account_type__c)s, %(Contacttype__pc)s,
                %(PersonBirthdate)s, %(PersonTitle)s, %(PersonDepartment)s,
                %(IsCustomerPortal)s, %(NumberOfEmployees)s, %(SicDesc)s,
                %(Bankverbindung_IBAN__c)s, %(Freistellungs_bescheinigung__c)s,
                %(Inside_ID__pc)s, %(Community_user_ID__pc)s, %(Default_community_userID__c)s,
                %(Community_user_calculation__c)s, %(Created_by_auto_flow__c)s,
                %(PersonIndividualId)s, %(PersonReportsToId)s,
                %(FlowToolKit__Latest_Form_Submission__c)s, %(FlowToolKit__Latest_Form_Submission__pc)s,
                %(Novumstate_campaign__pc)s,
                %(Description)s, %(Jigsaw)s, %(SourceSystemIdentifier)s,
                %(CreatedById)s, %(CreatedDate)s, %(LastModifiedById)s, %(LastModifiedDate)s,
                %(PersonLastCURequestDate)s, %(PersonLastCUUpdateDate)s
            )
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                last_modified_by_id = EXCLUDED.last_modified_by_id,
                last_modified_date = EXCLUDED.last_modified_date
        """,

        'objekt': """
            INSERT INTO objekts (
                id, name, objekt_id__c,
                address_street, address_city, address_state, address_postal_code, address_country,
                address_latitude, address_longitude,
                anzahl_we__c, anzahl_gew__c, anzahl_stellplaz__c, number_of_other_unit_types__c,
                apartment_unit__c, gewerbeeinheiten__c, stellplatze__c,
                in_management_this_year__c, in_management_next_year__c,
                vertragsende_letzter_sev_vertrag__c, verwaltervertragsende__c,
                difference_we__c, difference_gew__c, different_stellplatz__c,
                total_houses_and_offices__c, wohn_gewerbeeinheiten__c,
                check_today_with_last_sev_date__c, check_today_with_last_vertrage_date__c,
                city_group__c, management_level__c, property_manager__c, verwaltungsstatus__c,
                id_name__c, view_link__c,
                eigentumer__c, hausmeister__c, hausreinigung__c, elektro__c,
                heizung_sanitar__c, messdienstleister__c, schlusseldienst__c,
                versicherungsmakler__c, wasserschadenbehebung__c, winterdienst__c,
                management_companyold__c,
                hausverwaltung__c, objektbuchhalter__c, owner_id,
                contract_origin_objekt__c, name_system__c, priority__c, type_weg_mv__c,
                objekt_emailaddress__c, owners_emails__c, tenants_emails__c,
                picture__c, letzte_abrechnung__c, allgemeine_hinweise__c,
                status_objektbuchhaltung__c, checked_and_confirmed__c,
                impower__c,
                created_by_id, created_date, last_modified_by_id, last_modified_date
            ) VALUES (
                %(Id)s, %(Name)s, %(Objekt_ID__c)s,
                %(Address__Street__s)s, %(Address__City__s)s, %(Address__StateCode__s)s,
                %(Address__PostalCode__s)s, %(Address__CountryCode__s)s,
                %(Address__Latitude__s)s, %(Address__Longitude__s)s,
                %(Anzahl_WE__c)s, %(Anzahl_Gew__c)s, %(Anzahl_Stellplaz__c)s, %(Number_of_other_unit_types__c)s,
                %(Apartment_unit__c)s, %(Gewerbeeinheiten__c)s, %(Stellplatze__c)s,
                %(In_management_this_year__c)s, %(In_management_next_year__c)s,
                %(Vertragsende_letzter_SEV_Vertrag__c)s, %(Verwaltervertragsende__c)s,
                %(Difference_WE__c)s, %(Difference_GEw__c)s, %(Different_stellplatz__c)s,
                %(Total_houses_and_offices__c)s, %(Wohn_Gewerbeeinheiten__c)s,
                %(Check_today_with_last_SEV_date__c)s, %(Check_today_with_last_vertrage_date__c)s,
                %(City_group__c)s, %(Management_level__c)s, %(Property_manager__c)s, %(Verwaltungsstatus__c)s,
                %(ID_Name__c)s, %(view_link__c)s,
                %(Eigentumer__c)s, %(Hausmeister__c)s, %(Hausreinigung__c)s, %(Elektro__c)s,
                %(Heizung_Sanitar__c)s, %(Messdienstleister__c)s, %(Schlusseldienst__c)s,
                %(Versicherungsmakler__c)s, %(Wasserschadenbehebung__c)s, %(Winterdienst__c)s,
                %(Management_companyold__c)s,
                %(Hausverwaltung__c)s, %(Objektbuchhalter__c)s, %(OwnerId)s,
                %(Contract_origin_objekt__c)s, %(Name_system__c)s, %(Priority__c)s, %(Type_WEG_MV__c)s,
                %(Objekt_emailaddress__c)s, %(Owners_emails__c)s, %(Tenants_emails__c)s,
                %(Picture__c)s, %(Letzte_Abrechnung__c)s, %(Allgemeine_Hinweise__c)s,
                %(Status_Objektbuchhaltung__c)s, %(Checked_and_confirmed__c)s,
                %(Impower__c)s,
                %(CreatedById)s, %(CreatedDate)s, %(LastModifiedById)s, %(LastModifiedDate)s
            )
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                last_modified_by_id = EXCLUDED.last_modified_by_id,
                last_modified_date = EXCLUDED.last_modified_date
        """,

        'unit': """
            INSERT INTO units (
                id, name, description__c, objekt__c,
                type_of_unit__c, bauart__c, wohnflache__c, heizflache__c,
                accounting_id__c, impower_unit_id__c,
                count_active_sev_contracts__c, count_vertrage__c,
                last_vertrag_start_date__c, last_vertrage_end_date__c,
                objekt_text__c, owner_note__c, trigger__c,
                created_by_id, created_date, last_modified_by_id, last_modified_date
            ) VALUES (
                %(Id)s, %(Name)s, %(Description__c)s, %(Objekt__c)s,
                %(Type_of_unit__c)s, %(Bauart__c)s, %(Wohnflache__c)s, %(Heizflache__c)s,
                %(AccountingID__c)s, %(Impower_Unit_ID__c)s,
                %(Count_active_SEV_contracts__c)s, %(Count_vertrage__c)s,
                %(Last_vertrag_start_date__c)s, %(Last_vertrage_end_date__c)s,
                %(Objekt_text__c)s, %(Owner_note__c)s, %(Trigger__c)s,
                %(CreatedById)s, %(CreatedDate)s, %(LastModifiedById)s, %(LastModifiedDate)s
            )
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                last_modified_by_id = EXCLUDED.last_modified_by_id,
                last_modified_date = EXCLUDED.last_modified_date
        """
    }

    def __init__(self):
        """Initialize from environment variables"""
        # Salesforce config
        self.sf_api = SalesforceAPI(
            instance_url=os.getenv('SF_INSTANCE_URL', 'https://novumstate.my.salesforce.com'),
            api_version=os.getenv('SF_API_VERSION', 'v65.0'),
            access_token=os.getenv('SF_ACCESS_TOKEN')
        )

        # PostgreSQL config
        self.db = PostgresDB(
            host=os.getenv('PG_HOST', 'localhost'),
            port=int(os.getenv('PG_PORT', 5432)),
            database=os.getenv('PG_DATABASE'),
            user=os.getenv('PG_USER'),
            password=os.getenv('PG_PASSWORD')
        )

    def sync_all(self):
        """Sync all tables"""
        try:
            self.db.connect()
            logger.info("=== Starting full sync ===")

            # Sync in order (foreign key dependencies)
            tables = [
                ('account', 'accounts'),
                ('objekt', 'objekts'),
                ('unit', 'units')
            ]

            for query_key, table_name in tables:
                logger.info(f"\n--- Syncing {table_name} ---")
                records = self.sf_api.query(self.QUERIES[query_key])
                self.db.upsert_records(table_name, records, self.UPSERT_SQL[query_key])

            logger.info("\n=== ✓ Full sync completed ===")

        except Exception as e:
            logger.error(f"Sync failed: {e}")
            raise
        finally:
            self.db.close()

    def sync_incremental(self, hours: int = 24):
        """Sync only recent changes"""
        try:
            self.db.connect()
            logger.info(f"=== Starting incremental sync (last {hours}h) ===")

            # Calculate cutoff datetime
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            cutoff_str = cutoff.strftime('%Y-%m-%dT%H:%M:%SZ')

            # Sync in order
            tables = [
                ('account', 'accounts'),
                ('objekt', 'objekts'),
                ('unit', 'units')
            ]

            for query_key, table_name in tables:
                logger.info(f"\n--- Syncing {table_name} (modified since {cutoff_str}) ---")

                # Add time filter to query
                query = self.QUERIES[query_key].replace(
                    'WHERE IsDeleted = false',
                    f'WHERE IsDeleted = false AND LastModifiedDate > {cutoff_str}'
                )

                records = self.sf_api.query(query)
                self.db.upsert_records(table_name, records, self.UPSERT_SQL[query_key])

            logger.info("\n=== ✓ Incremental sync completed ===")

        except Exception as e:
            logger.error(f"Sync failed: {e}")
            raise
        finally:
            self.db.close()