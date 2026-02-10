import type { MGTFSFeed } from './models'
import { Feed } from './models'
import type {
    MGTFSAgencies,
    MGTFSRoutes,
    MGTFSSchedules,
    MGTFSStops,
    MGTFSTrips
} from './tables'
import {
    Agencies,
    Routes,
    Schedules,
    Stops,
    Trips
} from './tables'
import { unzip } from './util'


export type MGTFS = {
    agencies: MGTFSAgencies
    feed: MGTFSFeed
    name: string
    routes: MGTFSRoutes
    schedules: MGTFSSchedules
    stops: MGTFSStops
    trips: MGTFSTrips
}


export default class GTFS {

    agencies: Agencies
    feed: Feed
    name: string
    routes: Routes
    schedules: Schedules
    stops: Stops
    trips: Trips

    constructor (
                agencies: Agencies,
                feed: Feed,
                name: string,
                routes: Routes,
                schedules: Schedules,
                stops: Stops,
                trips: Trips
            ) {
        this.agencies = agencies
        this.feed = feed
        this.name = name
        this.routes = routes
        this.schedules = schedules
        this.stops = stops
        this.trips = trips
    }

    static fromMGTFS (data: MGTFS): GTFS {
        return new GTFS(
            new Agencies(data.agencies),
            new Feed(data.feed),
            data.name,
            new Routes(data.routes),
            new Schedules(data.schedules),
            new Stops(data.stops),
            Trips.fromMGTFS(data.trips)
        )
    }

    static async fromGTFS (
                name: string, data: Record<string, string>
            ): Promise<GTFS> {
        return GTFS.fromMGTFS({
            agencies: await Agencies.fromGTFS(data),
            feed: await Feed.fromGTFS(data),
            name,
            routes: await Routes.fromGTFS(data),
            schedules: await Schedules.fromGTFS(data),
            stops: await Stops.fromGTFS(data),
            trips: await Trips.fromGTFS(data)
        })
    }

    static async read (
                name: string,
                gtfsBlob?: Blob,
                gtfsSub?: string,
                gtfsURI?: string,
                mgtfs?: MGTFS
            ): Promise<GTFS> {
        if (mgtfs) return GTFS.fromMGTFS(mgtfs)
        if (gtfsBlob) {
            return await unzip(gtfsBlob, gtfsSub)
                .then(gtfs => GTFS.fromGTFS(name, gtfs))
        }
        return await fetch(gtfsURI!)
            .then(resp => resp.blob())
            .then(blob => unzip(blob, gtfsSub))
            .then(gtfs => GTFS.fromGTFS(name, gtfs))
    }
    

    _ref (trips: Trips): GTFS {
        return new GTFS(
            this.agencies,
            this.feed,
            this.name,
            this.routes,
            this.schedules,
            this.stops,
            trips
        )
    }

}