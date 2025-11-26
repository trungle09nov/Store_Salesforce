-- ============================================================================
-- Property Management Database Schema
-- Based on Salesforce data structure
-- ============================================================================

-- Drop existing tables (if any)
DROP TABLE IF EXISTS unit_owners CASCADE;
DROP TABLE IF EXISTS units CASCADE;
DROP TABLE IF EXISTS properties CASCADE;
DROP TABLE IF EXISTS clients CASCADE;
DROP TABLE IF EXISTS sync_metadata CASCADE;

-- ============================================================================
-- 1. CLIENTS TABLE (from extract.csv)
-- Stores both Person Accounts (owners/tenants) and Business Accounts
-- ============================================================================
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    sf_id VARCHAR(18) UNIQUE NOT NULL,

    -- Basic Info
    name VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    salutation VARCHAR(20),
    middle_name VARCHAR(100),
    suffix VARCHAR(50),

    -- Contact Information
    person_email VARCHAR(255),
    phone VARCHAR(50),
    mobile_phone VARCHAR(50),
    person_mobile_phone VARCHAR(50),
    person_home_phone VARCHAR(50),
    other_phone VARCHAR(50),
    other_mobile_phone VARCHAR(50),
    fax VARCHAR(50),
    website VARCHAR(255),

    -- Additional Emails
    email_2 VARCHAR(255),

    -- Account Type
    is_person_account BOOLEAN NOT NULL DEFAULT false,
    account_type VARCHAR(100), -- From Account_type__c
    account_source VARCHAR(100),
    contact_type VARCHAR(100), -- From Contacttype__pc

    -- Billing Address
    billing_street TEXT,
    billing_city VARCHAR(100),
    billing_postal_code VARCHAR(20),
    billing_state VARCHAR(100),
    billing_country VARCHAR(100),
    billing_latitude DECIMAL(10, 7),
    billing_longitude DECIMAL(10, 7),

    -- Mailing Address (for persons)
    person_mailing_street TEXT,
    person_mailing_city VARCHAR(100),
    person_mailing_postal_code VARCHAR(20),
    person_mailing_state VARCHAR(100),
    person_mailing_country VARCHAR(100),
    person_mailing_latitude DECIMAL(10, 7),
    person_mailing_longitude DECIMAL(10, 7),

    -- Shipping Address
    shipping_street TEXT,
    shipping_city VARCHAR(100),
    shipping_postal_code VARCHAR(20),
    shipping_state VARCHAR(100),
    shipping_country VARCHAR(100),

    -- Personal Information
    person_birthdate DATE,
    person_title VARCHAR(100),
    person_department VARCHAR(100),

    -- Business Information
    industry VARCHAR(100),
    number_of_employees INTEGER,
    description TEXT,

    -- Banking
    bank_iban VARCHAR(100), -- From Bankverbindung_IBAN__c

    -- Financial
    account_balance DECIMAL(15, 2), -- From Account_Balance__c

    -- Portal/Community
    is_customer_portal BOOLEAN DEFAULT false,
    community_user_id VARCHAR(50),
    default_community_user_id VARCHAR(50),

    -- Relationships
    parent_id VARCHAR(18), -- Reference to another Account
    master_record_id VARCHAR(18),

    -- System Fields
    owner_id VARCHAR(18),
    record_type_id VARCHAR(18),
    created_by_id VARCHAR(18),
    created_date TIMESTAMP,
    last_modified_by_id VARCHAR(18),
    last_modified_date TIMESTAMP,
    last_activity_date DATE,
    last_referenced_date TIMESTAMP,
    last_viewed_date TIMESTAMP,
    system_modstamp TIMESTAMP,

    -- Flags
    is_deleted BOOLEAN DEFAULT false,
    is_priority_record BOOLEAN DEFAULT false,
    created_by_auto_flow BOOLEAN DEFAULT false,

    -- Internal tracking
    synced_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT clients_sf_id_check CHECK (LENGTH(sf_id) = 18)
);

-- ============================================================================
-- 2. PROPERTIES TABLE (from extract_objekt.csv)
-- Stores building/property information
-- ============================================================================
CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    sf_id VARCHAR(18) UNIQUE NOT NULL,

    -- Basic Info
    name VARCHAR(255) NOT NULL,
    objekt_id VARCHAR(100), -- From Objekt_ID__c
    name_system VARCHAR(255), -- From Name_system__c
    id_name VARCHAR(255), -- From ID_Name__c (combined ID + Name)

    -- Address Information
    address_street TEXT,
    address_city VARCHAR(100),
    address_postal_code VARCHAR(20),
    address_state VARCHAR(100),
    address_country VARCHAR(100),
    address_latitude DECIMAL(10, 7),
    address_longitude DECIMAL(10, 7),

    -- Property Counts
    anzahl_we INTEGER, -- Number of residential units (Wohneinheiten)
    anzahl_gew INTEGER, -- Number of commercial units (Gewerbeeinheiten)
    anzahl_stellplatz INTEGER, -- Number of parking spaces (Stellplätze)
    gewerbeeinheiten INTEGER, -- Commercial units count
    wohn_gewerbeeinheiten INTEGER, -- Total residential + commercial
    total_houses_and_offices INTEGER,
    stellplatze INTEGER, -- Parking spaces
    apartment_unit INTEGER, -- Total apartment units

    -- Differences/Checks (calculated fields)
    difference_we INTEGER,
    difference_gew INTEGER,
    different_stellplatz INTEGER,

    -- Type & Status
    type_weg_mo VARCHAR(50), -- WEG (Wohnungseigentümergemeinschaft) or MO (Mietobjekt)
    verwaltungsstatus VARCHAR(100), -- Management status
    management_level VARCHAR(100),
    city_group VARCHAR(100),
    priority VARCHAR(50),

    -- Management Information
    hausverwaltung VARCHAR(18), -- Property management company (FK to clients)
    property_manager VARCHAR(18), -- Property manager (FK to user/contact)
    management_company_old VARCHAR(255),
    objektbuchhalter VARCHAR(18), -- Property accountant

    -- Service Providers (likely FKs to clients or contacts)
    eigentumer VARCHAR(18), -- Owner
    hausmeister VARCHAR(18), -- Caretaker
    hausreinigung VARCHAR(18), -- Cleaning service
    heizung_sanitar VARCHAR(18), -- Heating/plumbing
    elektro VARCHAR(18), -- Electrician
    messdienstleister VARCHAR(18), -- Meter reading service
    versicherungsmakler VARCHAR(18), -- Insurance broker
    wasserschadenbehebung VARCHAR(18), -- Water damage repair
    winterdienst VARCHAR(18), -- Winter service
    schlusseldienst VARCHAR(18), -- Key service

    -- Contact Information
    objekt_emailaddress VARCHAR(255),
    owners_emails TEXT, -- Comma-separated or JSON
    tenants_emails TEXT, -- Comma-separated or JSON

    -- Management Status
    in_management_this_year BOOLEAN DEFAULT false,
    in_management_next_year BOOLEAN DEFAULT false,

    -- Contract & Billing Information
    letzte_abrechnung VARCHAR(100), -- Last billing
    vertragsende_letzter_sev_vertrag DATE, -- End of last SEV contract
    verwaltervertragsende DATE, -- Property management contract end

    -- Notes & Additional Info
    allgemeine_hinweise TEXT, -- General notes
    status_objektbuchhaltung VARCHAR(100), -- Accounting status

    -- Checks
    checked_and_confirmed BOOLEAN DEFAULT false,
    check_today_with_last_sev_date BOOLEAN DEFAULT false,
    check_today_with_last_vertrage_date BOOLEAN DEFAULT false,

    -- Media
    picture_url TEXT,
    view_link TEXT,

    -- External IDs
    impower_id VARCHAR(100),

    -- System Fields
    owner_id VARCHAR(18),
    created_by_id VARCHAR(18),
    created_date TIMESTAMP,
    last_modified_by_id VARCHAR(18),
    last_modified_date TIMESTAMP,
    last_activity_date DATE,
    last_referenced_date TIMESTAMP,
    last_viewed_date TIMESTAMP,
    system_modstamp TIMESTAMP,
    is_deleted BOOLEAN DEFAULT false,

    -- Internal tracking
    synced_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT properties_sf_id_check CHECK (LENGTH(sf_id) = 18)
);

-- ============================================================================
-- 3. UNITS TABLE (from extract_units.csv)
-- Stores individual unit information (apartments, parking, commercial)
-- ============================================================================
CREATE TABLE units (
    id SERIAL PRIMARY KEY,
    sf_id VARCHAR(18) UNIQUE NOT NULL,

    -- Basic Info
    name VARCHAR(255) NOT NULL, -- Unit number/identifier
    description TEXT,

    -- Relationship to Property
    objekt_id VARCHAR(18) NOT NULL, -- FK to properties (sf_id)
    objekt_text VARCHAR(255), -- Text representation of property

    -- Unit Type & Details
    type_of_unit VARCHAR(10) NOT NULL, -- 'WE' (Wohnung/Apartment), 'St' (Stellplatz/Parking), 'GE' (Gewerbe/Commercial)
    bauart VARCHAR(100), -- Construction type

    -- Size Information
    wohnflache DECIMAL(10, 2), -- Living area in sqm (for WE)
    heizflache DECIMAL(10, 2), -- Heating area in sqm

    -- Contract Counts
    count_active_sev_contracts INTEGER DEFAULT 0, -- Active SEV contracts
    count_vertrage INTEGER DEFAULT 0, -- Total contracts

    -- Contract Dates
    last_vertrag_start_date DATE,
    last_vertrage_end_date DATE,

    -- Notes
    owner_note TEXT,

    -- External IDs
    accounting_id VARCHAR(100),
    impower_unit_id VARCHAR(100),

    -- Trigger field (might be used for automation)
    trigger_field TEXT,

    -- System Fields
    created_by_id VARCHAR(18),
    created_date TIMESTAMP,
    last_modified_by_id VARCHAR(18),
    last_modified_date TIMESTAMP,
    last_activity_date DATE,
    last_referenced_date TIMESTAMP,
    last_viewed_date TIMESTAMP,
    system_modstamp TIMESTAMP,
    is_deleted BOOLEAN DEFAULT false,

    -- Internal tracking
    synced_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT units_sf_id_check CHECK (LENGTH(sf_id) = 18),
    CONSTRAINT units_type_check CHECK (type_of_unit IN ('WE', 'St', 'GE')),
    FOREIGN KEY (objekt_id) REFERENCES properties(sf_id) ON DELETE CASCADE
);

-- ============================================================================
-- 4. UNIT_OWNERS TABLE (from owner_relat.csv)
-- Junction table linking clients (owners) to units
-- ============================================================================
CREATE TABLE unit_owners (
    id SERIAL PRIMARY KEY,
    sf_id VARCHAR(18) UNIQUE NOT NULL,

    -- Basic Info
    name VARCHAR(255) NOT NULL, -- Relationship name/identifier

    -- Relationships
    owner_id VARCHAR(18) NOT NULL, -- FK to clients (sf_id)
    unit_id VARCHAR(18) NOT NULL, -- FK to units (sf_id)
    parent_objekt_id VARCHAR(18), -- FK to properties (sf_id) - might be redundant

    -- Descriptions (denormalized for convenience)
    objekt_name VARCHAR(255),
    haus_unit_description TEXT,

    -- Ownership Period
    start_date DATE NOT NULL,
    end_date DATE NOT NULL, -- Often set to far future (2099-12-31) for active
    active BOOLEAN DEFAULT true,

    -- System Fields
    sf_owner_id VARCHAR(18), -- Salesforce record owner
    created_by_id VARCHAR(18),
    created_date TIMESTAMP,
    last_modified_by_id VARCHAR(18),
    last_modified_date TIMESTAMP,
    last_activity_date DATE,
    last_referenced_date TIMESTAMP,
    last_viewed_date TIMESTAMP,
    system_modstamp TIMESTAMP,
    is_deleted BOOLEAN DEFAULT false,

    -- Internal tracking
    synced_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT unit_owners_sf_id_check CHECK (LENGTH(sf_id) = 18),
    FOREIGN KEY (owner_id) REFERENCES clients(sf_id) ON DELETE CASCADE,
    FOREIGN KEY (unit_id) REFERENCES units(sf_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_objekt_id) REFERENCES properties(sf_id) ON DELETE SET NULL
);

-- ============================================================================
-- 5. SYNC_METADATA TABLE
-- Tracks synchronization status for incremental updates
-- ============================================================================
CREATE TABLE sync_metadata (
    object_name VARCHAR(100) PRIMARY KEY,
    last_sync_time TIMESTAMP NOT NULL,
    total_records INTEGER DEFAULT 0,
    total_errors INTEGER DEFAULT 0,
    last_error TEXT,
    last_successful_sync TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- INDEXES for Performance
-- ============================================================================

-- Clients indexes
CREATE INDEX idx_clients_name ON clients(name);
CREATE INDEX idx_clients_email ON clients(person_email);
CREATE INDEX idx_clients_is_person ON clients(is_person_account);
CREATE INDEX idx_clients_account_type ON clients(account_type);
CREATE INDEX idx_clients_billing_city ON clients(billing_city);
CREATE INDEX idx_clients_last_modified ON clients(last_modified_date);

-- Properties indexes
CREATE INDEX idx_properties_name ON properties(name);
CREATE INDEX idx_properties_objekt_id ON properties(objekt_id);
CREATE INDEX idx_properties_city ON properties(address_city);
CREATE INDEX idx_properties_type ON properties(type_weg_mo);
CREATE INDEX idx_properties_management ON properties(hausverwaltung);
CREATE INDEX idx_properties_last_modified ON properties(last_modified_date);

-- Units indexes
CREATE INDEX idx_units_objekt ON units(objekt_id);
CREATE INDEX idx_units_name ON units(name);
CREATE INDEX idx_units_type ON units(type_of_unit);
CREATE INDEX idx_units_last_modified ON units(last_modified_date);

-- Unit_owners indexes
CREATE INDEX idx_unit_owners_owner ON unit_owners(owner_id);
CREATE INDEX idx_unit_owners_unit ON unit_owners(unit_id);
CREATE INDEX idx_unit_owners_property ON unit_owners(parent_objekt_id);
CREATE INDEX idx_unit_owners_active ON unit_owners(active);
CREATE INDEX idx_unit_owners_dates ON unit_owners(start_date, end_date);

-- ============================================================================
-- VIEWS for Common Queries
-- ============================================================================

-- View: Active unit ownership with full details
CREATE OR REPLACE VIEW v_active_unit_ownership AS
SELECT
    uo.sf_id as ownership_sf_id,
    uo.name as ownership_name,
    c.sf_id as owner_sf_id,
    c.name as owner_name,
    c.person_email as owner_email,
    c.phone as owner_phone,
    u.sf_id as unit_sf_id,
    u.name as unit_name,
    u.type_of_unit,
    u.wohnflache as unit_sqm,
    p.sf_id as property_sf_id,
    p.name as property_name,
    p.address_city,
    p.address_street,
    uo.start_date,
    uo.end_date,
    uo.active
FROM unit_owners uo
JOIN clients c ON uo.owner_id = c.sf_id
JOIN units u ON uo.unit_id = u.sf_id
JOIN properties p ON u.objekt_id = p.sf_id
WHERE uo.active = true
  AND uo.is_deleted = false
  AND c.is_deleted = false
  AND u.is_deleted = false
  AND p.is_deleted = false;

-- View: Property summary with unit counts
CREATE OR REPLACE VIEW v_property_summary AS
SELECT
    p.sf_id,
    p.name as property_name,
    p.objekt_id,
    p.address_city,
    p.address_street,
    p.type_weg_mo,
    p.anzahl_we as declared_residential_units,
    p.anzahl_gew as declared_commercial_units,
    p.anzahl_stellplatz as declared_parking_spaces,
    COUNT(DISTINCT CASE WHEN u.type_of_unit = 'WE' THEN u.id END) as actual_residential_units,
    COUNT(DISTINCT CASE WHEN u.type_of_unit = 'GE' THEN u.id END) as actual_commercial_units,
    COUNT(DISTINCT CASE WHEN u.type_of_unit = 'St' THEN u.id END) as actual_parking_spaces,
    COUNT(DISTINCT u.id) as total_units,
    SUM(CASE WHEN u.type_of_unit = 'WE' THEN u.wohnflache ELSE 0 END) as total_residential_sqm,
    COUNT(DISTINCT uo.owner_id) as unique_owners
FROM properties p
LEFT JOIN units u ON p.sf_id = u.objekt_id AND u.is_deleted = false
LEFT JOIN unit_owners uo ON u.sf_id = uo.unit_id AND uo.active = true AND uo.is_deleted = false
WHERE p.is_deleted = false
GROUP BY p.id, p.sf_id, p.name, p.objekt_id, p.address_city, p.address_street,
         p.type_weg_mo, p.anzahl_we, p.anzahl_gew, p.anzahl_stellplatz;

-- View: Client portfolio (all units owned by each client)
CREATE OR REPLACE VIEW v_client_portfolio AS
SELECT
    c.sf_id as client_sf_id,
    c.name as client_name,
    c.person_email,
    c.is_person_account,
    COUNT(DISTINCT uo.unit_id) as total_units_owned,
    COUNT(DISTINCT u.objekt_id) as properties_count,
    STRING_AGG(DISTINCT p.name, ', ' ORDER BY p.name) as properties_list,
    SUM(CASE WHEN u.type_of_unit = 'WE' THEN 1 ELSE 0 END) as residential_units,
    SUM(CASE WHEN u.type_of_unit = 'GE' THEN 1 ELSE 0 END) as commercial_units,
    SUM(CASE WHEN u.type_of_unit = 'St' THEN 1 ELSE 0 END) as parking_spaces,
    SUM(CASE WHEN u.type_of_unit = 'WE' THEN u.wohnflache ELSE 0 END) as total_residential_sqm
FROM clients c
JOIN unit_owners uo ON c.sf_id = uo.owner_id AND uo.active = true AND uo.is_deleted = false
JOIN units u ON uo.unit_id = u.sf_id AND u.is_deleted = false
JOIN properties p ON u.objekt_id = p.sf_id AND p.is_deleted = false
WHERE c.is_deleted = false
GROUP BY c.sf_id, c.name, c.person_email, c.is_person_account;

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to get active owners for a unit
CREATE OR REPLACE FUNCTION get_unit_owners(unit_sf_id VARCHAR(18))
RETURNS TABLE (
    owner_name VARCHAR(255),
    owner_email VARCHAR(255),
    start_date DATE,
    end_date DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.name,
        c.person_email,
        uo.start_date,
        uo.end_date
    FROM unit_owners uo
    JOIN clients c ON uo.owner_id = c.sf_id
    WHERE uo.unit_id = unit_sf_id
      AND uo.active = true
      AND uo.is_deleted = false
      AND c.is_deleted = false
    ORDER BY uo.start_date DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get all units in a property
CREATE OR REPLACE FUNCTION get_property_units(property_sf_id VARCHAR(18))
RETURNS TABLE (
    unit_name VARCHAR(255),
    unit_type VARCHAR(10),
    unit_sqm DECIMAL(10, 2),
    owner_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        u.name,
        u.type_of_unit,
        u.wohnflache,
        COUNT(DISTINCT uo.owner_id)
    FROM units u
    LEFT JOIN unit_owners uo ON u.sf_id = uo.unit_id
        AND uo.active = true
        AND uo.is_deleted = false
    WHERE u.objekt_id = property_sf_id
      AND u.is_deleted = false
    GROUP BY u.id, u.name, u.type_of_unit, u.wohnflache
    ORDER BY u.name;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE clients IS 'Stores all clients including owners and tenants (from Salesforce Account object)';
COMMENT ON TABLE properties IS 'Stores property/building information (from Salesforce Property__c custom object)';
COMMENT ON TABLE units IS 'Stores individual units - apartments, parking spaces, commercial units (from Salesforce Unit__c)';
COMMENT ON TABLE unit_owners IS 'Junction table linking owners to their units (from Salesforce ownership relationship object)';
COMMENT ON TABLE sync_metadata IS 'Tracks synchronization status with Salesforce';

COMMENT ON COLUMN units.type_of_unit IS 'WE = Wohneinheit (Residential), St = Stellplatz (Parking), GE = Gewerbe (Commercial)';
COMMENT ON COLUMN properties.type_weg_mo IS 'WEG = Wohnungseigentümergemeinschaft (Condominium), MO = Mietobjekt (Rental Property)';