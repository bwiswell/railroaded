import { formatOptionalDate, parseOptionalDate } from '../util'


export type GTFSFeed = {
    default_lang?: string
    feed_contact_email?: string
    feed_contact_url?: string
    feed_end_date?: string
    feed_lang: string
    feed_start_date?: string
    feed_version?: string
    publisher_name: string
    publisher_url: string
}


export type MGTFSFeed = {
    contact_email?: string
    contact_url?: string
    default_lang?: string
    end_date?: string
    lang: string
    publisher_name: string
    publisher_url: string
    start_date?: string
    version?: string
}


export default class Feed {

    contactEmail?: string
    contactURL?: string
    defaultLang?: string
    endDate?: Date
    lang: string
    publisherName: string
    publisherURL: string
    startDate?: Date
    version?: string

    constructor (data: MGTFSFeed) {
        this.contactEmail = data.contact_email
        this.contactURL = data.contact_url
        this.defaultLang = data.default_lang
        this.endDate = parseOptionalDate(data.end_date)
        this.lang = data.lang
        this.publisherName = data.publisher_name
        this.publisherURL = data.publisher_url
        this.startDate = parseOptionalDate(data.start_date)
        this.version = data.version
    }

    static fromGTFS (data: GTFSFeed): MGTFSFeed {
        return {
            contact_email: data.feed_contact_email,
            contact_url: data.feed_contact_url,
            default_lang: data.default_lang,
            end_date: data.feed_end_date,
            lang: data.feed_lang,
            publisher_name: data.publisher_name,
            publisher_url: data.publisher_url,
            start_date: data.feed_start_date,
            version: data.feed_version
        }
    }

    toMGTFS (): MGTFSFeed {
        return {
            contact_email: this.contactEmail,
            contact_url: this.contactURL,
            default_lang: this.defaultLang,
            end_date: formatOptionalDate(this.endDate),
            lang: this.lang,
            publisher_name: this.publisherName,
            publisher_url: this.publisherURL,
            start_date: formatOptionalDate(this.startDate),
            version: this.version
        }
    }

}