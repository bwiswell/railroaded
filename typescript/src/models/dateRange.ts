import { GTFSCalendar } from '../types'
import { formatDate, parseDate } from '../util'


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

    static fromGTFS (data: GTFSCalendar): MGTFSDateRange {
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