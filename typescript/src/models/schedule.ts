import type { GTFSCalendarDate } from '../types'
import { formatDate, includesDay, parseDate, split } from '../util'

import DateRange, { GTFSDateRange, MGTFSDateRange } from './dateRange'


export type MGTFSSchedule = {
    service_id: string
    additions: string[]
    exceptions: string[]
    ranges: MGTFSDateRange[]
}


/**
 * A GTFS model that defines a schedule for a transit service.
 * 
 * @property serviceId - the unique ID of the service associated with the
 * schedule
 * @property additions - a list of dates on which additional service is offered
 * @property end - the end date of the transit schedule
 * @property exceptions - a list of dates on which service is suspended
 * @property ranges - a list of `DateRange` records associated with the schedule
 * @property start - the start date of the transit schedule
 */
export default class Schedule {

    serviceId: string
    additions: Date[]
    end: Date
    exceptions: Date[]
    ranges: DateRange[]
    start: Date

    constructor (data: MGTFSSchedule) {
        this.serviceId = data.service_id
        this.additions = data.additions.map(parseDate)
        this.exceptions = data.exceptions.map(parseDate)
        this.ranges = data.ranges.map(range => new DateRange(range))
        this.start = new Date(
            Math.min(...this.ranges.map(range => range.start.getTime()))
        )
        this.end = new Date(
            Math.max(...this.ranges.map(range => range.end.getTime()))
        )
    }

    static fromGTFS (
                serviceId: string,
                ranges: GTFSDateRange[],
                calDates: GTFSCalendarDate[]
            ): MGTFSSchedule {
        const splitExceptions = split(
            calDates, 
            calDate => calDate.exception_type === 1
        )
        return {
            service_id: serviceId,
            additions: splitExceptions.truthy.map(calDate => calDate.date),
            exceptions: splitExceptions.falsy.map(calDate => calDate.date),
            ranges: ranges.map(DateRange.fromGTFS)
        }
    }

    toMGTFS (): MGTFSSchedule {
        return {
            service_id: this.serviceId,
            additions: this.additions.map(formatDate),
            exceptions: this.exceptions.map(formatDate),
            ranges: this.ranges.map(range => range.toMGTFS())
        }
    }

    /**
     * Returns a `boolean` indicating if the service is active on `date`.
     * 
     * Returns `false` if `date` is outside of the GTFS dataset's feed range.
     * 
     * @param date - the `Date` to check for active service
     * @returns a `boolean` indicating if the service is active on `date`
     */
    active (date: Date): boolean {
        if (date < this.start || date > this.end) return false
        if (includesDay(date, this.additions)) return true
        if (includesDay(date, this.exceptions)) return false
        return this.ranges.some(
            range => (
                date >= range.start && 
                date <= range.end && 
                range.schedule[(date.getDay() - 1) % 7]
            )
        ) 
    }
}