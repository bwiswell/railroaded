import { loadList } from '../util/util'

import { 
    Route, 
    routeName,
    stopContinuity,
    transitType
} from '../types/types'

/**
 * Utility class for loading and accessing a table mapping `string` IDs to
 * `Route` records.
 * 
 * @property routes - a `List` of `Route` records in the `Routes` table
 * @property data - a `Record` mapping `string` IDs to `Route` records
 * @property ids - a `List` of all `string` IDs in the `Routes` table
 * 
 * @see Route
 */
export default class Routes {
    routes: Route[]
    data: Record<string, Route>
    ids: string[]

    constructor (data: Record<string, Route>) {
        this.routes = Object.values(data)
        this.data = data
        this.ids = Object.keys(data)
    }

    /**
     * Asynchronously loads an `Routes` table populated from the GTFS data at
     * `path`.
     *
     * @param path - the path to the GTFS dataset
     * @returns a `Promise` resolving to an `Routes` table populated from the
     * GTFS data at `path`
     */
    static async from_gtfs (path: string): Promise<Routes> {
        const routes = await loadList<Route>(
            `${path}/routes.txt`,
            {
                interpolateCols: {
                    'name': routeName
                },
                intCols: ['sortIdx'],
                renameCols: {
                    'route_id': 'id',
                    'agency_id': 'agencyId',
                    'route_color': 'color',
                    'route_desc': 'desc',
                    'route_long_name': 'longName',
                    'route_short_name': 'shortName',
                    'route_sort_order': 'sortIdx',
                    'route_text_color': 'textColor',
                    'route_type': 'type',
                    'route_url': 'url'
                },
                transformEnums: {
                    'dropoffs': stopContinuity,
                    'pickups': stopContinuity,
                    'type': transitType
                }

            }
        )
        return new Routes(
            routes.reduce(
                (acc, Route) => {
                    acc[Route.id] = Route
                    return acc
                },
                {} as Record<string, Route>
            )
        )
    }

    /**
     * Returns the `Route` record with ID `id` if it exists, otherwise returns
     * `undefined`.
     * 
     * @param id - the `string` id associated with the `Route` record to 
     * retrieve
     * @returns the `Route` record associated with `id` if it exists,
     * otherwise `undefined`
     */
    get (id: string): Route | undefined {
        return this.data[id]
    }
}