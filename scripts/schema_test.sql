-- =====================================================
-- DATABASE SCHEMA FOR SALESFORCE INTEGRATION
-- Tables: Account, Objekt, Unit, Owner_Relationship
-- =====================================================

-- =====================================================
-- 1. ACCOUNT TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS accounts (
    -- Primary Key
    id VARCHAR(18) PRIMARY KEY,

    -- Account Name & Components
    name VARCHAR(255) NOT NULL,
    salutation VARCHAR(40),
    first_name VARCHAR(40),
    last_name VARCHAR(80),
    middle_name VARCHAR(40),
    suffix VARCHAR(40),

    -- Basic Account Info
    account_number VARCHAR(40),
    account_site VARCHAR(80),

    -- Ownership & Record Management
    owner_id VARCHAR(18) NOT NULL,
    record_type_id VARCHAR(18),
    parent_id VARCHAR(18),

    -- Financial Information
    account_balance DECIMAL(18, 0),
    annual_revenue DECIMAL(18, 0),

    -- Contact Information - Person Account
    person_email VARCHAR(255),
    person_mobile_phone VARCHAR(40),
    person_home_phone VARCHAR(40),
    person_other_phone VARCHAR(40),
    person_assistant_name VARCHAR(40),
    person_assistant_phone VARCHAR(40),

    -- Contact Information - Business/Custom
    phone VARCHAR(40),
    email__c VARCHAR(255),
    email_2__pc VARCHAR(255),
    email_2__c VARCHAR(255),
    mobile_phone__c VARCHAR(40),
    other_mobile_phone__pc VARCHAR(40),
    other_phone__c VARCHAR(40),
    fax VARCHAR(40),
    website VARCHAR(255),

    -- Address Fields - Billing
    billing_street TEXT,
    billing_city VARCHAR(100),
    billing_state VARCHAR(100),
    billing_postal_code VARCHAR(20),
    billing_country VARCHAR(100),
    billing_latitude DECIMAL(10, 7),
    billing_longitude DECIMAL(10, 7),

    -- Address Fields - Shipping
    shipping_street TEXT,
    shipping_city VARCHAR(100),
    shipping_state VARCHAR(100),
    shipping_postal_code VARCHAR(20),
    shipping_country VARCHAR(100),
    shipping_latitude DECIMAL(10, 7),
    shipping_longitude DECIMAL(10, 7),

    -- Address Fields - Person Mailing
    person_mailing_street TEXT,
    person_mailing_city VARCHAR(100),
    person_mailing_state VARCHAR(100),
    person_mailing_postal_code VARCHAR(20),
    person_mailing_country VARCHAR(100),
    person_mailing_latitude DECIMAL(10, 7),
    person_mailing_longitude DECIMAL(10, 7),

    -- Address Fields - Person Other
    person_other_street TEXT,
    person_other_city VARCHAR(100),
    person_other_state VARCHAR(100),
    person_other_postal_code VARCHAR(20),
    person_other_country VARCHAR(100),
    person_other_latitude DECIMAL(10, 7),
    person_other_longitude DECIMAL(10, 7),

    -- Picklist Fields
    account_source VARCHAR(100),
    industry VARCHAR(100),
    ownership VARCHAR(100),
    rating VARCHAR(50),
    type VARCHAR(100),
    person_lead_source VARCHAR(100),
    person_gender_identity VARCHAR(50),
    person_pronouns VARCHAR(50),
    contact_import_sourc__pc VARCHAR(100),

    -- Multi-Select Picklist
    account_type__c TEXT,
    contacttype__pc TEXT,

    -- Personal Information
    person_birthdate DATE,
    person_title VARCHAR(80),
    person_department VARCHAR(80),

    -- Preferences & Flags
    person_do_not_call BOOLEAN DEFAULT FALSE,
    person_has_opted_out_of_email BOOLEAN DEFAULT FALSE,
    person_has_opted_out_of_fax BOOLEAN DEFAULT FALSE,
    is_customer_portal BOOLEAN DEFAULT FALSE,

    -- Business Information
    number_of_employees INTEGER,
    sic VARCHAR(20),
    sic_desc VARCHAR(80),
    ticker_symbol VARCHAR(20),

    -- German/Custom Fields
    bankverbindung_iban__c VARCHAR(40),
    freistellungs_bescheinigung__c VARCHAR(10),

    -- Community/Portal Fields
    inside_id__pc VARCHAR(40),
    community_user_id__pc VARCHAR(20),
    default_community_userid__c VARCHAR(50),
    community_user_calculation__c INTEGER,
    created_by_auto_flow__c INTEGER,

    -- Lookup Relationships
    person_individual_id VARCHAR(18),
    person_reports_to_id VARCHAR(18),
    flowtoolkit__latest_form_submission__c VARCHAR(18),
    flowtoolkit__latest_form_submission__pc VARCHAR(18),
    novumstate_campaign__pc VARCHAR(18),

    -- System Fields
    description TEXT,
    tier VARCHAR(2),
    jigsaw VARCHAR(20),
    source_system_identifier VARCHAR(85),

    -- Audit Fields
    created_by_id VARCHAR(18) NOT NULL,
    created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_modified_by_id VARCHAR(18) NOT NULL,
    last_modified_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Stay-in-Touch Fields
    person_last_cu_request_date TIMESTAMP,
    person_last_cu_update_date TIMESTAMP
);

-- Account Indexes
CREATE INDEX idx_accounts_name ON accounts(name);
CREATE INDEX idx_accounts_owner_id ON accounts(owner_id);
CREATE INDEX idx_accounts_record_type_id ON accounts(record_type_id);
CREATE INDEX idx_accounts_parent_id ON accounts(parent_id);
CREATE INDEX idx_accounts_source_system_identifier ON accounts(source_system_identifier);
CREATE INDEX idx_accounts_form_submission_c ON accounts(flowtoolkit__latest_form_submission__c);
CREATE INDEX idx_accounts_form_submission_pc ON accounts(flowtoolkit__latest_form_submission__pc);
CREATE INDEX idx_accounts_campaign ON accounts(novumstate_campaign__pc);

-- =====================================================
-- 2. OBJEKT TABLE (Property/Building)
-- =====================================================
CREATE TABLE IF NOT EXISTS objekts (
    -- Primary Key
    id VARCHAR(18) PRIMARY KEY,

    -- Basic Info
    name VARCHAR(80) NOT NULL,
    objekt_id__c VARCHAR(20),

    -- Address (Compound field in Salesforce)
    address_street TEXT,
    address_city VARCHAR(100),
    address_state VARCHAR(100),
    address_postal_code VARCHAR(20),
    address_country VARCHAR(100),
    address_latitude DECIMAL(10, 7),
    address_longitude DECIMAL(10, 7),

    -- Property Details
    anzahl_we__c INTEGER,
    anzahl_gew__c INTEGER,
    anzahl_stellplaz__c INTEGER,
    number_of_other_unit_types__c INTEGER,

    -- Roll-up Summary Fields
    apartment_unit__c INTEGER,
    gewerbeeinheiten__c INTEGER,
    stellplatze__c INTEGER,

    -- Contract Related
    total_vertrage__c INTEGER,
    in_management_this_year__c INTEGER,
    in_management_next_year__c INTEGER,
    vertragsende_letzter_sev_vertrag__c DATE,
    verwaltervertragsende__c DATE,

    -- Formula Fields
    difference_we__c INTEGER,
    difference_gew__c INTEGER,
    different_stellplatz__c INTEGER,
    total_houses_and_offices__c INTEGER,
    wohn_gewerbeeinheiten__c INTEGER,
    check_today_with_last_sev_date__c BOOLEAN,
    check_today_with_last_vertrage_date__c BOOLEAN,
    city_group__c VARCHAR(100),
    management_level__c VARCHAR(100),
    property_manager__c VARCHAR(255),
    verwaltungsstatus__c VARCHAR(100),
    id_name__c VARCHAR(255),
    view_link__c TEXT,

    -- Lookups to Accounts (Service Providers)
    eigentumer__c VARCHAR(18),
    eigentumer2__c VARCHAR(18),
    hausmeister__c VARCHAR(18),
    hausreinigung__c VARCHAR(18),
    elektro__c VARCHAR(18),
    heizung_sanitar__c VARCHAR(18),
    messdienstleister__c VARCHAR(18),
    schlusseldienst__c VARCHAR(18),
    versicherungsmakler__c VARCHAR(18),
    wasserschadenbehebung__c VARCHAR(18),
    winterdienst__c VARCHAR(18),
    management_companyold__c VARCHAR(18),

    -- Lookup to Business Brand
    hausverwaltung__c VARCHAR(18),

    -- Lookup to User
    objektbuchhalter__c VARCHAR(18),
    owner_id VARCHAR(18) NOT NULL,

    -- Picklists
    contract_origin_objekt__c VARCHAR(100),
    name_system__c VARCHAR(100),
    priority__c VARCHAR(50),
    type_weg_mv__c VARCHAR(50),

    -- Email & Communication
    objekt_emailaddress__c VARCHAR(255),
    owners_emails__c TEXT,
    tenants_emails__c TEXT,
    advisory_board_emails__c TEXT,

    -- Additional Info
    picture__c VARCHAR(255),
    letzte_abrechnung__c TEXT,
    allgemeine_hinweise__c TEXT,
    status_objektbuchhaltung__c TEXT,

    -- Flags
    checked_and_confirmed__c BOOLEAN DEFAULT FALSE,
    not_included_in_reports__c BOOLEAN DEFAULT FALSE,

    -- Integration
    impower__c VARCHAR(255),

    -- Audit Fields
    created_by_id VARCHAR(18) NOT NULL,
    created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_modified_by_id VARCHAR(18) NOT NULL,
    last_modified_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Objekt Indexes
CREATE INDEX idx_objekts_name ON objekts(name);
CREATE INDEX idx_objekts_owner_id ON objekts(owner_id);
CREATE INDEX idx_objekts_eigentumer ON objekts(eigentumer__c);
CREATE INDEX idx_objekts_eigentumer2 ON objekts(eigentumer2__c);
CREATE INDEX idx_objekts_hausmeister ON objekts(hausmeister__c);
CREATE INDEX idx_objekts_hausreinigung ON objekts(hausreinigung__c);
CREATE INDEX idx_objekts_hausverwaltung ON objekts(hausverwaltung__c);
CREATE INDEX idx_objekts_elektro ON objekts(elektro__c);
CREATE INDEX idx_objekts_heizung_sanitar ON objekts(heizung_sanitar__c);
CREATE INDEX idx_objekts_messdienstleister ON objekts(messdienstleister__c);
CREATE INDEX idx_objekts_management_company ON objekts(management_companyold__c);
CREATE INDEX idx_objekts_objektbuchhalter ON objekts(objektbuchhalter__c);
CREATE INDEX idx_objekts_schlusseldienst ON objekts(schlusseldienst__c);
CREATE INDEX idx_objekts_versicherungsmakler ON objekts(versicherungsmakler__c);
CREATE INDEX idx_objekts_wasserschadenbehebung ON objekts(wasserschadenbehebung__c);
CREATE INDEX idx_objekts_winterdienst ON objekts(winterdienst__c);

-- =====================================================
-- 3. UNIT TABLE (Apartment/Commercial Unit)
-- =====================================================
CREATE TABLE IF NOT EXISTS units (
    -- Primary Key
    id VARCHAR(18) PRIMARY KEY,

    -- Basic Info
    name VARCHAR(80) NOT NULL,
    description__c VARCHAR(80),

    -- Master-Detail Relationship to Objekt (REQUIRED)
    objekt__c VARCHAR(18) NOT NULL,

    -- Unit Details
    type_of_unit__c VARCHAR(50),
    bauart__c VARCHAR(50),
    wohnflache__c DECIMAL(5, 2),
    heizflache__c DECIMAL(5, 2),

    -- IDs & Integration
    accounting_id__c VARCHAR(20),
    impower_unit_id__c VARCHAR(99),

    -- Contract Information
    count_active_sev_contracts__c INTEGER,
    count_vertrage__c INTEGER,
    last_vertrag_start_date__c DATE,
    last_vertrage_end_date__c DATE,

    -- Lookups
    oldeigentumer__c VARCHAR(18),

    -- Formula Fields
    objekt_text__c VARCHAR(255),

    -- Additional Info
    owner_note__c VARCHAR(200),
    trigger__c INTEGER,

    -- Audit Fields
    created_by_id VARCHAR(18) NOT NULL,
    created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_modified_by_id VARCHAR(18) NOT NULL,
    last_modified_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Key Constraint
    CONSTRAINT fk_unit_objekt FOREIGN KEY (objekt__c) REFERENCES objekts(id) ON DELETE CASCADE
);

-- Unit Indexes
CREATE INDEX idx_units_name ON units(name);
CREATE INDEX idx_units_objekt ON units(objekt__c);
CREATE INDEX idx_units_oldeigentumer ON units(oldeigentumer__c);
CREATE INDEX idx_units_type ON units(type_of_unit__c);

-- =====================================================
-- 4. OWNER_RELATIONSHIP TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS owner_relationships (
    id VARCHAR(18) PRIMARY KEY,
    name VARCHAR(80) NOT NULL,

    -- 3 Lookups chính
    owner__c VARCHAR(18),         -- ✅ Lookup to Account
    unit__c VARCHAR(18),          -- ✅ Lookup to Unit
    parent_objekt__c VARCHAR(18), -- ✅ Lookup to Objekt

    owner_id VARCHAR(18) NOT NULL,
    start_date__c DATE,
    end_date__c DATE,

    active__c BOOLEAN,
    haus_unit_description__c VARCHAR(255),
    objekt_name__c VARCHAR(255),

    created_by_id VARCHAR(18) NOT NULL,
    created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_modified_by_id VARCHAR(18) NOT NULL,
    last_modified_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Keys cho cả 3 lookups
    CONSTRAINT fk_owner_relationship_owner
        FOREIGN KEY (owner__c) REFERENCES accounts(id),
    CONSTRAINT fk_owner_relationship_unit
        FOREIGN KEY (unit__c) REFERENCES units(id) ON DELETE CASCADE,
    CONSTRAINT fk_owner_relationship_objekt
        FOREIGN KEY (parent_objekt__c) REFERENCES objekts(id) ON DELETE CASCADE
);

-- Owner Relationship Indexes
CREATE INDEX idx_owner_relationships_name ON owner_relationships(name);
CREATE INDEX idx_owner_relationships_owner_id ON owner_relationships(owner_id);
CREATE INDEX idx_owner_relationships_owner ON owner_relationships(owner__c);
CREATE INDEX idx_owner_relationships_unit ON owner_relationships(unit__c);
CREATE INDEX idx_owner_relationships_objekt ON owner_relationships(parent_objekt__c);
CREATE INDEX idx_owner_relationships_dates ON owner_relationships(start_date__c, end_date__c);

-- =====================================================
-- FOREIGN KEY CONSTRAINTS
-- =====================================================

-- Account relationships
ALTER TABLE accounts ADD CONSTRAINT fk_account_parent
    FOREIGN KEY (parent_id) REFERENCES accounts(id);

-- Objekt to Account relationships
ALTER TABLE objekts ADD CONSTRAINT fk_objekt_eigentumer
    FOREIGN KEY (eigentumer__c) REFERENCES accounts(id);
ALTER TABLE objekts ADD CONSTRAINT fk_objekt_eigentumer2
    FOREIGN KEY (eigentumer2__c) REFERENCES accounts(id);
ALTER TABLE objekts ADD CONSTRAINT fk_objekt_hausmeister
    FOREIGN KEY (hausmeister__c) REFERENCES accounts(id);
ALTER TABLE objekts ADD CONSTRAINT fk_objekt_hausreinigung
    FOREIGN KEY (hausreinigung__c) REFERENCES accounts(id);
ALTER TABLE objekts ADD CONSTRAINT fk_objekt_elektro
    FOREIGN KEY (elektro__c) REFERENCES accounts(id);
ALTER TABLE objekts ADD CONSTRAINT fk_objekt_heizung
    FOREIGN KEY (heizung_sanitar__c) REFERENCES accounts(id);
ALTER TABLE objekts ADD CONSTRAINT fk_objekt_messdienstleister
    FOREIGN KEY (messdienstleister__c) REFERENCES accounts(id);
ALTER TABLE objekts ADD CONSTRAINT fk_objekt_schlusseldienst
    FOREIGN KEY (schlusseldienst__c) REFERENCES accounts(id);
ALTER TABLE objekts ADD CONSTRAINT fk_objekt_versicherungsmakler
    FOREIGN KEY (versicherungsmakler__c) REFERENCES accounts(id);
ALTER TABLE objekts ADD CONSTRAINT fk_objekt_wasserschadenbehebung
    FOREIGN KEY (wasserschadenbehebung__c) REFERENCES accounts(id);
ALTER TABLE objekts ADD CONSTRAINT fk_objekt_winterdienst
    FOREIGN KEY (winterdienst__c) REFERENCES accounts(id);
ALTER TABLE objekts ADD CONSTRAINT fk_objekt_management_company
    FOREIGN KEY (management_companyold__c) REFERENCES accounts(id);

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE accounts IS 'Salesforce Account object - Business and Person accounts';
COMMENT ON TABLE objekts IS 'Property/Building object - manages real estate properties';
COMMENT ON TABLE units IS 'Unit object - individual apartments, commercial spaces, or parking spots within an Objekt';
COMMENT ON TABLE owner_relationships IS 'Junction table linking Accounts (owners) to Units with date ranges';

COMMENT ON COLUMN units.objekt__c IS 'Master-Detail relationship - Unit cannot exist without Objekt';
COMMENT ON COLUMN objekts.apartment_unit__c IS 'Roll-up summary: COUNT of Units where type is apartment';
COMMENT ON COLUMN objekts.total_vertrage__c IS 'Roll-up summary: COUNT of all Customer contracts';
COMMENT ON COLUMN owner_relationships.active__c IS 'Formula: TRUE if current date is between start_date__c and end_date__c';
