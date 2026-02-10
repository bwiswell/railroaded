import { Route } from '../models'
import type { GTFSRoute, MGTFSRoute } from '../models'
import { loadList } from '../util'


export type MGTFSRoutes = {
    data: Record<string, MGTFSRoute>
}


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

    constructor (data: MGTFSRoutes) {
        this.data = Object.keys(data.data).reduce(
            (prev, curr) => {
                prev[curr] = new Route(data.data[curr]!)
                return prev
            },
            {} as Record<string, Route>
        )
        this.routes = Object.values(this.data)
        this.ids = Object.keys(this.data)
    }

    /**
     * Asynchronously loads an `Routes` table populated from the GTFS data at
     * `path`.
     *
     * @param path - the path to the GTFS dataset
     * @returns a `Promise` resolving to an `Routes` table populated from the
     * GTFS data at `path`
     */
    static async fromGTFS (
                data: Record<string, string>
            ): Promise<MGTFSRoutes> {
        const routes = await loadList<GTFSRoute>(data['routes.txt']!)
            .then(gtfsRoutes => gtfsRoutes.map(
                route => Route.fromGTFS(route)
            ))
        return {
            data: routes.reduce(
                (prev, curr) => {
                    prev[curr.id] = curr
                    return prev
                },
                {} as Record<string, MGTFSRoute>
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
                {} as Record<string, MGTFSRoute>
            )
        }
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