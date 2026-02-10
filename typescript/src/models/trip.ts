import type { Accessibility, BikesAllowed, Time } from "../types";
import { 
    fromAccessibility, 
    fromBikesAllowed, 
    toAccessibility,
    toBikesAllowed 
} from "../types";
import { parseOptionalInt } from "../util";

import { GTFSStopTime } from "./stopTime";
import Timetable, { MGTFSTimetable } from "./timetable";


export type GTFSTrip = {
    trip_id: string
    block_id?: string
    route_id: string
    service_id: string
    shape_id?: string
    bikes_allowed?: string
    direction_id?: string
    trip_headsign?: string
    trip_short_name?: string
    wheelchair_accessible?: string
}


export type MGTFSTrip = {
    id: string
    block_id?: string
    route_id: string
    service_id: string
    shape_id?: string
    accessibility: number
    bikes: number
    direction?: boolean
    headsign?: string
    short_name?: string
    timetable: MGTFSTimetable
}


export class Trip {

    id: string
    blockId?: string
    routeId: string
    serviceId: string
    shapeId?: string
    accessibility: Accessibility
    bikes: BikesAllowed
    direction?: boolean
    headsign?: string
    shortName?: string
    timetable: Timetable

    constructor (data: MGTFSTrip) {
        this.id = data.id
        this.blockId = data.block_id
        this.routeId = data.route_id
        this.serviceId = data.service_id
        this.shapeId = data.shape_id
        this.accessibility = toAccessibility(data.accessibility)
        this.bikes = toBikesAllowed(data.bikes)
        this.direction = data.direction
        this.headsign = data.headsign
        this.shortName = data.short_name
        this.timetable = new Timetable(data.timetable)
    }

    static fromGTFS (data: GTFSTrip, stops: GTFSStopTime[]): MGTFSTrip {
        const timetable = Timetable.fromGTFS(stops)
        return {
            ...data,
            id: data.trip_id,
            accessibility: parseOptionalInt(
                data.wheelchair_accessible,
                fromAccessibility('unknown')
            ),
            bikes: parseOptionalInt(
                data.bikes_allowed,
                fromBikesAllowed('unknown')
            ),
            direction: data.direction_id ? 
                Boolean(parseInt(data.direction_id)) : 
                undefined,
            headsign: data.trip_headsign,
            short_name: data.trip_short_name,
            timetable
        }
    }

    toMGTFS (): MGTFSTrip {
        return {
            id: this.id,
            block_id: this.blockId,
            route_id: this.routeId,
            service_id: this.serviceId,
            shape_id: this.shapeId,
            accessibility: fromAccessibility(this.accessibility),
            bikes: fromBikesAllowed(this.bikes),
            direction: this.direction,
            headsign: this.headsign,
            short_name: this.shortName,
            timetable: this.timetable.toMGTFS()
        }
    }


    between (start: Time, end: Time): boolean { 
        return this.timetable.between(start, end) 
    }

    connects (stopAId: string, stopBId: string): boolean {
        return this.timetable.connects(stopAId, stopBId)
    }

    through (stopId: string): boolean {
        return this.timetable.through(stopId)
    }

}