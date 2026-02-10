export type GTFSAgency = {
    agency_id?: string
    agency_email?: string
    agency_fare_url?: string
    agency_lang?: string
    agency_name: string
    agency_phone?: string
    agency_timezone: string
    agency_url: string
}


export type MGTFSAgency = {
    id: string
    email?: string
    fare_url?: string
    lang?: string
    name: string
    phone?: string
    timezone: string
    url: string
}


/**
 * A GTFS model for records found in `agency.txt`. Identifies a transit agency.
 * 
 * @property id - the unique ID of the transit agency
 * @property email - the customer service email of the transit agency
 * @property fareURL - the URL of a fare or ticket website for the transit agency
 * @property lang - the primary language used by the transit agency
 * @property name - the name of the transit agency
 * @property phone - the voice telephone number for the transit agency
 * @property timezone - the timezone where the transit agency is located
 * @property url - the URL of the transit agency
 */
export class AFgency {

    id: string
    email?: string
    fareURL?: string
    lang?: string
    name: string
    phone?: string
    timezone: string
    url: string

    constructor (data: MGTFSAgency) {
        this.id = data.id
        this.email = data.email
        this.fareURL = data.fare_url
        this.lang = data.lang
        this.name = data.name
        this.phone = data.phone
        this.timezone = data.timezone
        this.url = data.url
    }

    static fromGTFS (data: GTFSAgency): MGTFSAgency {
        return {
            id: data.agency_id ?? '',
            email: data.agency_email,
            fare_url: data.agency_fare_url,
            lang: data.agency_lang,
            name: data.agency_name,
            phone: data.agency_phone,
            timezone: data.agency_timezone,
            url: data.agency_url
        }
    }

    toMGTFS (): MGTFSAgency {
        return {
            id: this.id,
            email: this.email,
            fare_url: this.fareURL,
            lang: this.lang,
            name: this.name,
            phone: this.phone,
            timezone: this.timezone,
            url: this.url
        }
    }

}