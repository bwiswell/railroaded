import { formatDate, parseDate } from '../util'


export type GTFSDateRange = {
    service_id: string
    end_date: string
    friday: string
    monday: string
    saturday: string
    start_date: string
    sunday: string
    thursday: string
    tuesday: string
    wednesday: string
}


export type MGTFSDateRange = {
    end: string
    schedule: boolean[]
    start: string
}


export default class DataRange {

    end: Date
    schedule: boolean[]
    start: Date

    constructor (data: MGTFSDateRange) {
        this.end = parseDate(data.end)
        this.schedule = data.schedule
        this.start = parseDate(data.start)
    }

    static fromGTFS (data: GTFSDateRange): MGTFSDateRange {
        return {
            ...data,
            end: data.end_date,
            start: data.start_date,
            schedule: [
                data.monday,
                data.tuesday,
                data.wednesday,
                data.thursday,
                data.friday,
                data.saturday,
                data.sunday
            ].map(parseInt).map(Boolean)
        }
    }

    toMGTFS (): MGTFSDateRange {
        return {
            end: formatDate(this.end),
            schedule: this.schedule,
            start: formatDate(this.start)
        }
    }
}