import { Schedule } from '../models'
import type { MGTFSSchedule } from '../models'
import type { GTFSCalendar, GTFSCalendarDate } from '../types'
import { loadList, unique } from '../util'


export type MGTFSRoutes = {
    data: Record<string, MGTFSSchedule>
}


/**
 * Utility class for loading and accessing a table mapping `string` IDs to
 * `Schedule` records.
 * 
 * @property schedules - a `List` of `Schedule` records in the `Schedules` table
 * @property data - a `Record` mapping `string` IDs to `Schedule` records
 * @property ids - a `List` of all `string` IDs in the `Schedules` table
 * 
 * @see Schedule
 */
export default class Schedules {
    
    schedules: Schedule[]
    data: Record<string, Schedule>
    serviceIds: string[]

    constructor (data: MGTFSRoutes) {
        this.data = Object.keys(data.data).reduce(
            (prev, curr) => {
                prev[curr] = new Schedule(data.data[curr]!)
                return prev
            },
            {} as Record<string, Schedule>
        )
        this.schedules = Object.values(this.data)
        this.serviceIds = Object.keys(this.data)
    }

    /**
     * Asynchronously loads an `Schedules` table populated from the GTFS data
     * at `path`.
     *
     * @param path - the path to the GTFS dataset
     * @returns a `Promise` resolving to an `Schedules` table populated from
     * the GTFS data at `path`
     */
    static async fromGTFS (path: string): Promise<MGTFSRoutes> {
        const calendars = await loadList<GTFSCalendar>(`${path}/calendar.txt`)
        const dates = await loadList<GTFSCalendarDate>(
            `${path}/calendar_dates.txt`
        )
        const serviceIds = unique(calendars.map(cal => cal.service_id))
        return {
            data: serviceIds.reduce(
                (prev, curr) => {
                    prev[curr] = Schedule.fromGTFS(
                        curr, 
                        calendars.filter(cal => cal.service_id === curr),
                        dates.filter(date => date.service_id === curr)
                    )
                    return prev
                },
                {} as Record<string, MGTFSSchedule>
            )
        }  
    }

    toMGTFS (): MGTFSRoutes {
        return {
            data: Object.keys(this.data).reduce(
                (prev, curr) => {
                    prev[curr] = this.data[curr]!.toMGTFS()
                    return prev
                },
                {} as Record<string, MGTFSSchedule>
            )
        }
    }


    /**
     * Returns the `Schedule` record with ID `id` if it exists, otherwise returns
     * `undefined`.
     * 
     * @param id - the `string` id associated with the `Schedule` record to 
     * retrieve
     * @returns the `Schedule` record associated with `id` if it exists,
     * otherwise `undefined`
     */
    get (id: string): Schedule | undefined {
        return this.data[id]
    }


    onDate (date: Date): string[] {
        return this.schedules
            .filter(schedule => schedule.active(date))
            .map(schedule => schedule.serviceId)
    }
}