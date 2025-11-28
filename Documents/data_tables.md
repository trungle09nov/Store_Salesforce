# Account
| FIELD LABEL | FIELD NAME | DATA TYPE | CONTROLLING FIELD | INDEXED |
| :--- | :--- | :--- | :--- | :--- |
| Account Balance | Account_Balance__c | Currency(18, 0) | | |
| Account Name | Name | Name | | ✓ |
| &nbsp;&nbsp;&nbsp;&nbsp;Salutation | Salutation | Picklist | | |
| &nbsp;&nbsp;&nbsp;&nbsp;First Name | FirstName | Text(40) | | |
| &nbsp;&nbsp;&nbsp;&nbsp;Last Name | LastName | Text(80) | | |
| &nbsp;&nbsp;&nbsp;&nbsp;Middle Name | MiddleName | Text(40) | | |
| &nbsp;&nbsp;&nbsp;&nbsp;Suffix | Suffix | Text(40) | | |
| Account Number | AccountNumber | Text(40) | | |
| Account Owner | OwnerId | Lookup(User) | | ✓ |
| Account Record Type | RecordTypeId | Record Type | | ✓ |
| Account Site | Site | Text(80) | | |
| Account Source | AccountSource | Picklist | | |
| Account type | Account_type__c | Picklist (Multi-Select) | | |
| Annual Revenue | AnnualRevenue | Currency(18, 0) | | |
| Assistant | PersonAssistantName | Text(40) | | |
| Asst. Phone | PersonAssistantPhone | Phone | | |
| Bankverbindung (IBAN) | Bankverbindung_IBAN__c | Text(40) | | |
| Billing Address | BillingAddress | Address | | |
| Birthdate | PersonBirthdate | Date | | |
| Community user calculation | Community_user_calculation__c | Number(1, 0) | | |
| Community user ID | Community_user_ID__pc | Text(20) | | |
| Contact import source | Contact_import_sourc__pc | Picklist | | |
| Contact type | Contacttype__pc | Picklist (Multi-Select) | | |
| Created By | CreatedById | Lookup(User) | | |
| Created by auto flow | Created_by_auto_flow__c | Number(1, 0) | | |
| Customer Portal Account | IsCustomerPortal | Checkbox | | |
| Data.com Key | Jigsaw | Text(20) | | |
| Default community userID | Default_community_userID__c | Text(50) | | |
| Department | PersonDepartment | Text(80) | | |
| Description | Description | Long Text Area(32000) | | |
| Do Not Call | PersonDoNotCall | Checkbox | | |
| Einstein Account Tier | Tier | Text(2) | | |
| Email | Email__c | Email | | |
| Email | PersonEmail | Email | | |
| Email 2 | Email_2__pc | Email | | |
| Email 2 | Email_2__c | Email | | |
| Email Opt Out | PersonHasOptedOutOfEmail | Checkbox | | |
| Employees | NumberOfEmployees | Number(8, 0) | | |
| Fax | Fax | Phone | | |
| Fax Opt Out | PersonHasOptedOutOfFax | Checkbox | | |
| Freistellungs-bescheinigung | Freistellungs_bescheinigung__c | Text(10) | | |
| Gender Identity | PersonGenderIdentity | Picklist | | |
| Home Phone | PersonHomePhone | Phone | | |
| Individual | PersonIndividualId | Lookup(Individual) | | |
| Industry | Industry | Picklist | | |
| Inside ID | Inside_ID__pc | Text(40) | | |
| Last Modified By | LastModifiedById | Lookup(User) | | |
| Last Stay-in-Touch Request Date | PersonLastCURequestDate | Date/Time | | |
| Last Stay-in-Touch Save Date | PersonLastCUUpdateDate | Date/Time | | |
| Latest Form Submission | FlowToolkit__Latest_Form_Submission__c | Lookup(Form Submission) | | ✓ |
| Latest Form Submission | FlowToolkit__Latest_Form_Submission__pc | Lookup(Form Submission) | | ✓ |
| Lead Source | PersonLeadSource | Picklist | | |
| Mailing Address | PersonMailingAddress | Address | | |
| Mobile | PersonMobilePhone | Phone | | |
| Mobile phone | Mobile_phone__c | Phone | | |
| Novumstate campaign | Novumstate_campaign__pc | Lookup(Novumstate campaign) | | ✓ |
| Other Address | PersonOtherAddress | Address | | |
| Other mobile phone | Other_mobile_phone__pc | Phone | | |
| Other phone | Other_phone__c | Phone | | |
| Other Phone | PersonOtherPhone | Phone | | |
| Ownership | Ownership | Picklist | | |
| Parent Account | ParentId | Hierarchy | | ✓ |
| Phone | Phone | Phone | | |
| Pronouns | PersonPronouns | Picklist | | |
| Rating | Rating | Picklist | | |
| Reports To | PersonReportsToId | Lookup(Contact) | | |
| Shipping Address | ShippingAddress | Address | | |
| SIC Code | Sic | Text(20) | | |
| SIC Description | SicDesc | Text(80) | | |
| Source System ID | SourceSystemIdentifier | Text(85) | | ✓ |
| Ticker Symbol | TickerSymbol | Text(20) | | |
| Title | PersonTitle | Text(80) | | |
| Type | Type | Picklist | | |
| Website | Website | URL(255) | | |

# Objekt
| FIELD LABEL | FIELD NAME | DATA TYPE | CONTROLLING FIELD | INDEXED |
| :--- | :--- | :--- | :--- | :--- |
| Address | Address__c | Address | | |
| Advisory board emails | Advisory_board_emails__c | Long Text Area(99999) | | |
| Allgemeine Hinweise | Allgemeine_Hinweise__c | Long Text Area(32768) | | |
| Anzahl Gew. | Anzahl_Gew__c | Number(4, 0) | | |
| Anzahl Stellplaz | Anzahl_Stellplaz__c | Number(4, 0) | | |
| Anzahl WE | Anzahl_WE__c | Number(4, 0) | | |
| Apartment unit | Apartment_unit__c | Roll-Up Summary (COUNT Unit) | | |
| Check today with last SEV date | Check_today_with_last_SEV_date__c | Formula (Checkbox) | | |
| Check today with last vertrage date | Check_today_with_last_vertrage_date__c | Formula (Checkbox) | | |
| Checked and confirmed | Checked_and_confirmed__c | Checkbox | | |
| City group | City_group__c | Formula (Text) | | |
| Contract origin (objekt) | Contract_origin_objekt__c | Picklist | | |
| Created By | CreatedById | Lookup(User) | | |
| Difference GEw | Difference_GEw__c | Formula (Number) | | |
| Difference WE | Difference_WE__c | Formula (Number) | | |
| Different stellplatz | Different_stellplatz__c | Formula (Number) | | |
| Eigentümer | Eigentumer__c | Lookup(Account) | | ✓ |
| Eigentümer | Eigentumer2__c | Lookup(Account) | | ✓ |
| Elektro | Elektro__c | Lookup(Account) | | ✓ |
| Gewerbeeinheiten | Gewerbeeinheiten__c | Roll-Up Summary (COUNT Unit) | | |
| Hausmeister | Hausmeister__c | Lookup(Account) | | ✓ |
| Hausreinigung | Hausreinigung__c | Lookup(Account) | | ✓ |
| Hausverwaltung | Hausverwaltung__c | Lookup(Business Brand) | | ✓ |
| Heizung / Sanitär | Heizung_Sanitar__c | Lookup(Account) | | ✓ |
| Impower_propertyId | Impower__c | Text(255) | | |
| In management next year | In_management_next_year__c | Roll-Up Summary (COUNT Customer contract) | | |
| In management this year | In_management_this_year__c | Roll-Up Summary (COUNT Customer contract) | | |
| Last Modified By | LastModifiedById | Lookup(User) | | |
| Letzte Abrechnung | Letzte_Abrechnung__c | Text Area(255) | | |
| Management company (old) | Management_companyold__c | Lookup(Account) | | ✓ |
| Management level | Management_level__c | Formula (Text) | | |
| Messdienstleister | Messdienstleister__c | Lookup(Account) | | ✓ |
| Name system | Name_system__c | Picklist | | |
| Not included in reports | Not_included_in_reports__c | Checkbox | | |
| Number of other unit types | Number_of_other_unit_types__c | Number(3, 0) | | |
| Object_Priority | Priority__c | Picklist | | |
| Objekt email address | Objekt_emailaddress__c | Email | | |
| Objekt ID | Objekt_ID__c | Text(20) | | |
| Objekt ID + Name | ID_Name__c | Formula (Text) | | |
| Objekt Name | Name | Text(80) | | ✓ |
| Objekt Picture | Picture__c | URL(255) | | |
| Objektbuchhalter | Objektbuchhalter__c | Lookup(User) | | ✓ |
| Owner | OwnerId | Lookup(User,Group) | | ✓ |
| Owners emails | Owners_emails__c | Long Text Area(32768) | | |
| Property manager | Property_manager__c | Formula (Text) | | |
| Schlüsseldienst | Schlusseldienst__c | Lookup(Account) | | ✓ |
| Status Objektbuchhaltung | Status_Objektbuchhaltung__c | Long Text Area(10000) | | |
| Stellplätze | Stellplatze__c | Roll-Up Summary (COUNT Unit) | | |
| Tenants emails | Tenants_emails__c | Long Text Area(32768) | | |
| Total houses and offices | Total_houses_and_offices__c | Formula (Number) | | |
| Total vertrage | Total_vertrage__c | Roll-Up Summary (COUNT Customer contract) | | |
| Type WEG/MV | Type_WEG_MV__c | Picklist | | |
| Versicherungsmakler | Versicherungsmakler__c | Lookup(Account) | | ✓ |
| Vertragsende letzter SEV Vertrag | Vertragsende_letzter_SEV_Vertrag__c | Roll-Up Summary (MAX Customer contract) | | |
| Verwaltervertragsende | Verwaltervertragsende__c | Roll-Up Summary (MAX Customer contract) | | |
| Verwaltungsstatus | Verwaltungsstatus__c | Formula (Text) | | |
| view link | view_link__c | Formula (Text) | | |
| Wasserschadenbehebung | Wasserschadenbehebung__c | Lookup(Account) | | ✓ |
| Winterdienst | Winterdienst__c | Lookup(Account) | | ✓ |
| Wohn + Gewerbeeinheiten | Wohn_Gewerbeeinheiten__c | Formula (Number) | | |

# Unit
| FIELD LABEL | FIELD NAME | DATA TYPE | CONTROLLING FIELD | INDEXED |
| :--- | :--- | :--- | :--- | :--- |
| Bauart | Bauart__c | Picklist | | |
| Count active SEV contracts | Count_active_SEV_contracts__c | Number(2, 0) | | |
| Count vertrage | Count_vertrage__c | Number(3, 0) | | |
| Created By | CreatedById | Lookup(User) | | |
| Description | Description__c | Text(80) | | |
| Hausunit Name | Name | Text(80) | | ✓ |
| Heizfläche | Heizflache__c | Number(5, 2) | | |
| ID Buchhaltung | AccountingID__c | Text(20) | | |
| Impower Unit ID | Impower_Unit_ID__c | Text(99) | | |
| Last Modified By | LastModifiedById | Lookup(User) | | |
| Last vertrag start date | Last_vertrag_start_date__c | Date | | |
| Last vertrage end date | Last_vertrage_end_date__c | Date | | |
| Objekt | Objekt__c | Master-Detail(Objekt) | | ✓ |
| Objekt text | Objekt_text__c | Formula (Text) | | |
| Old Eigentumer | Oldeigentumer__c | Lookup(Contact) | | ✓ |
| Owner note | Owner_note__c | Text(200) | | |
| Trigger | Trigger__c | Number(1, 0) | | |
| Type of unit | Type_of_unit__c | Picklist | | |
| Wohnfläche / Gewerbefläche | Wohnflache__c | Number(5, 2) | | |

# owner relationship
| FIELD LABEL | FIELD NAME | DATA TYPE | CONTROLLING FIELD | INDEXED |
| :--- | :--- | :--- | :--- | :--- |
| Active | Active__c | Formula (Checkbox) | | |
| Created By | CreatedById | Lookup(User) | | |
| End date | End_date__c | Date | | |
| Haus unit description | Haus_unit_description__c | Formula (Text) | | |
| Last Modified By | LastModifiedById | Lookup(User) | | |
| Objekt name | Objekt_name__c | Formula (Text) | | |
| Owner | Owner__c | Lookup(Account) | | ✓ |
| Owner | OwnerId | Lookup(User,Group) | | ✓ |
| Owner relationship name | Name | Text(80) | | ✓ |
| Parent Objekt | Parent_Objekt__c | Lookup(Objekt) | | ✓ |
| Start date | Start_date__c | Date | | |
| Unit | Unit__c | Lookup(Unit) | | ✓ |