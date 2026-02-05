export const accessibilities = [
    'unknown',
    'accessible',
    'not_accessible'
] as const
/**
 * An enumeration describing the accessibility of a transit location.
 */
export type Accessibility = typeof accessibilities[number]
export const accessibility = (accessibility: number): Accessibility => 
    accessibilities[accessibility] as Accessibility


export const stopContinuities = [
    'continuous',
    'none',
    'via_phone',
    'via_driver'
] as const
/**
 * An enumeration describing the stop continuity of a route.
 */
export type StopContinuity = typeof stopContinuities[number]
export const stopContinuity = (continuity: number): StopContinuity => 
    stopContinuities[continuity] as StopContinuity


export const transitTypes = [
    'light-rail', 
    'subway', 
    'rail', 
    'bus', 
    'ferry', 
    'cable_tram', 
    'cable_car', 
    'funicular',
    'trolleybus',
    'monorail'
] as const
/**
 * An enumeration describing the transit type of a route.
 */
export type TransitType = typeof transitTypes[number]
export const transitType = (type: number): TransitType =>
    transitTypes[type] as TransitType


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
export type Agency = {
    id: string
    email?: string
    fareURL?: string
    lang?: string
    name: string
    phone?: string
    timezone: string
    url: string
}


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