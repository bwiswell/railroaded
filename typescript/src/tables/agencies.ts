import { loadList } from '../util/csv'

import type { Agency } from '../types/types'

/**
 * Utility class for loading and accessing a table mapping `string` IDs to
 * `Agency` records.
 * 
 * @property agencies - a `List` of `Agency` records in the `Agencies` table
 * @property data - a `Record` mapping `string` IDs to `Agency` records
 * @property ids - a `List` of all `string` IDs in the `Agencies` table
 * 
 * @see Agency
 */
export default class Agencies {
    /**
     * 
     */
    agencies: Agency[]
    data: Record<string, Agency>
    ids: string[]

    constructor (data: Record<string, Agency>) {
        this.agencies = Object.values(data)
        this.data = data
        this.ids = Object.keys(data)
    }

    /**
     * Asynchronously loads an `Agencies` table populated from the GTFS data at
     * `path`.
     *
     * @param path - the path to the GTFS dataset
     * @returns a `Promise` resolving to an `Agencies` table populated from the
     * GTFS data at `path`
     */
    static async from_gtfs (path: string): Promise<Agencies> {
        const agencies = await loadList<Agency>(
            `${path}/agency.txt`,
            {
                renameCols: {
                    'agency_id': 'id',
                    'agency_email': 'email',
                    'agency_fare_url': 'fareURL',
                    'agency_lang': 'lang',
                    'agency_name': 'name',
                    'agency_phone': 'phone',
                    'agency_timezone': 'timezone',
                    'agency_url': 'url'
                }
            }
        )
        return new Agencies(
            agencies.reduce(
                (acc, agency) => {
                    acc[agency.id] = agency
                    return acc
                },
                {} as Record<string, Agency>
            )
        )
    }

    /**
     * Returns the `Agency` record with ID `id` if it exists, otherwise returns
     * `undefined`.
     * 
     * @param id - the `string` id associated with the `Agency` record to 
     * retrieve
     * @returns the `Agency` record associated with `id` if it exists,
     * otherwise `undefined`
     */
    get (id: string): Agency | undefined {
        return this.data[id]
    }
}