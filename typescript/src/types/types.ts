








/**
 * A GTFS model for records found in `routes.txt`. Identifies a transit route.
 * 
 * @property id - the unique ID of the route
 * @property agencyId - the unique ID of the agency the route belongs to
 * @property color - the color associated with the route
 * @property desc - a description of the route
 * @property dropoffs - the continuity of dropoffs along the route
 * @property longName - the full name of the route
 * @property name - the name of the route
 * @property networkId - the unique ID of the network the route belongs to
 * @property pickups - the continuity of pickups along the route
 * @property shortName - the short name of the route
 * @property sortIdx - the sort index of the route
 * @property textColor - the color to use for text drawn against `color`
 * @property type - the `TransitType` of the route
 * @property url - the URL of a webpage about the route
 */
export type Route = {
    id: string
    agencyId: string
    color: string
    desc?: string
    dropoffs: StopContinuity
    longName?: string
    name: string
    networkId?: string
    pickups: StopContinuity
    shortName?: string
    sortIdx: number
    textColor: string
    type: TransitType
    url?: string
}
export const routeName = (route: Partial<Route>): string => 
    route.longName ?? route.shortName ?? ''


