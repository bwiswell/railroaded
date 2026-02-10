import type { GTFSStopTime, GTFSTrip, MGTFSTrip } from '../models'
import { Trip } from '../models'
import type { Time } from '../types'
import { filterObject, loadList } from '../util'


export type MGTFSTrips = {
    data: Record<string, MGTFSTrip>
}


/**
 * Utility class for loading and accessing a table mapping `string` IDs to
 * `Trip` records.
 * 
 * @property data - a `Record` mapping `string` IDs to `Trip` records
 * @property ids - an array of all `string` IDs in the `Trips` table
 * @property trips - an array of `Trip` records in the `Trips` table
 * 
 * @see Trip
 */
export default class Trips {

    data: Record<string, Trip>
    ids: string[]
    trips: Trip[]

    constructor (data: Record<string, Trip>) {
        this.data = data
        this.ids = Object.keys(this.data)
        this.trips = Object.values(this.data)
    }

    
    static async fromGTFS (
                data: Record<string, string>
            ): Promise<MGTFSTrips> {
        const stopTimes = await loadList<GTFSStopTime>(data['stop_times.txt']!)
        const trips = await loadList<GTFSTrip>(data['trips.txt']!)

        return {
            data: trips.reduce(
                (prev, curr) => {
                    prev[curr.trip_id] = Trip.fromGTFS(
                        curr, 
                        stopTimes.filter(st => st.trip_id === curr.trip_id)
                    )
                    return prev
                },
                {} as Record<string, MGTFSTrip>
            )
        }
    }

    static fromMGTFS (data: MGTFSTrips): Trips {
        return new Trips(
            Object.keys(data.data).reduce(
                (prev, curr) => {
                    prev[curr] = new Trip(data.data[curr]!)
                    return prev
                },
                {} as Record<string, Trip>
            )
        )
    }

    toGTFS (): MGTFSTrips {
        return {
            data: Object.keys(this.data).reduce(
                (prev, curr) => {
                    prev[curr] = this.data[curr]!.toMGTFS()
                    return prev
                },
                {} as Record<string, MGTFSTrip>
            )
        }
    }
    

    get (id: string): Trip | undefined {
        return this.data[id]
    }


    between (start: Time, end: Time): Trips {
        return new Trips(
            filterObject(this.data, trip => trip.between(start, end))
        )
    }

    connecting (stopAId: string, stopBId: string): Trips {
        return new Trips(
            filterObject(this.data, trip => trip.connects(stopAId, stopBId))
        )
    }

    onDate (serviceIds: string[]): Trips {
        return new Trips(
            filterObject(
                this.data, 
                trip => serviceIds.includes(trip.serviceId)
            )
        )
    }

    onRoute (routeId: string): Trips {
        return new Trips(
            filterObject(this.data, trip => trip.routeId === routeId)
        )
    }

    through (stopId: string): Trips {
        return new Trips(
            filterObject(this.data, trip => trip.through(stopId))
        )
    }
}