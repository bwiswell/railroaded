import type { StopContinuity, TransitType } from "../types"
import { 
    fromStopContinuity, 
    fromTransitType, 
    toStopContinuity, 
    toTransitType 
} from "../types"
import { parseOptionalInt } from '../util'


export type GTFSRoute = {
    route_id: string
    agency_id?: string
    network_id?: string
    dropoffs?: string
    pickups?: string
    route_color?: string
    route_desc?: string
    route_long_name?: string
    route_short_name?: string
    route_type: string
    route_url?: string
    sort_idx?: string
    text_color?: string
}


export type MGTFSRoute = {
    id: string
    agency_id: string
    network_id?: string
    color: string
    desc?: string
    dropoffs: number
    long_name?: string
    pickups: number
    short_name?: string
    sort_idx: number
    text_color: string
    type: number
    url?: string
}


/**
 * A GTFS model for records found in `routes.txt`. Identifies a transit route.
 * 
 * @property id - the unique ID of the route
 * @property agencyId - the unique ID of the agency the route belongs to
 * @property networkId - the unique ID of the network the route belongs to
 * @property color - the color associated with the route
 * @property desc - a description of the route
 * @property dropoffs - the continuity of dropoffs along the route
 * @property longName - the full name of the route
 * @property name - the name of the route
 * @property pickups - the continuity of pickups along the route
 * @property shortName - the short name of the route
 * @property sortIdx - the sort index of the route
 * @property textColor - the color to use for text drawn against `color`
 * @property type - the `TransitType` of the route
 * @property url - the URL of a webpage about the route
 */
export default class Route {

    id: string
    agencyId: string
    networkId?: string
    color: string
    desc?: string
    dropoffs: StopContinuity
    longName?: string
    name: string
    pickups: StopContinuity
    shortName?: string
    sortIdx: number
    textColor: string
    type: TransitType
    url?: string

    constructor (data: MGTFSRoute) {
        this.id = data.id
        this.agencyId = data.agency_id
        this.networkId = data.network_id
        this.color = data.color
        this.desc = data.desc
        this.dropoffs = toStopContinuity(data.dropoffs)
        this.longName = data.long_name
        this.name = data.long_name ?? data.short_name ?? ''
        this.pickups = toStopContinuity(data.pickups)
        this.shortName = data.short_name
        this.sortIdx = data.sort_idx
        this.textColor = data.text_color
        this.type = toTransitType(data.type)
        this.url = data.url
    }

    static fromGTFS (data: GTFSRoute): MGTFSRoute {
        return {
            id: data.route_id,
            agency_id: data.agency_id ?? '',
            network_id: data.network_id,
            color: data.route_color ?? 'FFFFFF',
            desc: data.route_desc,
            dropoffs: parseOptionalInt(
                data.dropoffs,
                fromStopContinuity('none')
            ),
            long_name: data.route_long_name,
            pickups: parseOptionalInt(
                data.pickups,
                fromStopContinuity('none')
            ),
            short_name: data.route_short_name,
            sort_idx: parseOptionalInt(data.sort_idx, 0),
            text_color: data.text_color ?? '000000',
            type: parseInt(data.route_type),
            url: data.route_url
        }
    }

    toMGTFS (): MGTFSRoute {
        return {
            id: this.id,
            agency_id: this.agencyId,
            network_id: this.networkId,
            color: this.color,
            desc: this.desc,
            dropoffs: fromStopContinuity(this.dropoffs),
            long_name: this.longName,
            pickups: fromStopContinuity(this.pickups),
            short_name: this.shortName,
            sort_idx: this.sortIdx,
            text_color: this.textColor,
            type: fromTransitType(this.type),
            url: this.url
        }
    }

}