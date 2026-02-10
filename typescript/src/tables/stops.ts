import type { GTFSStop, MGTFSStop } from '../models'
import { Stop } from '../models'
import { loadList } from '../util'


export type MGTFSStops = {
    data: Record<string, MGTFSStop>
}


/**
 * Utility class for loading and accessing a table mapping `string` IDs to
 * `Stop` records.
 * 
 * @property data - a `Record` mapping `string` IDs to `Stop` records
 * @property ids - an array of all `string` IDs in the `Stops` table
 * @property names = a n array of all `Stop.name` values in the `Stops` table
 * @property stops - an array of `Stop` records in the `Stops` table
 * 
 * @see Stop
 */
export default class Stops {

    data: Record<string, Stop>
    ids: string[]
    names: string[]
    stops: Stop[]

    constructor (data: MGTFSStops) {
        this.data = Object.keys(data.data).reduce(
            (prev, curr) => {
                prev[curr] = new Stop(data.data[curr]!)
                return prev
            },
            {} as Record<string, Stop>
        )
        this.ids = Object.keys(this.data)
        this.names = Object.values(this.data).map(stop => stop.name)
        this.stops = Object.values(this.data)
    }

    
    static async fromGTFS (
                data: Record<string, string>
            ): Promise<MGTFSStops> {
        const stops = await loadList<GTFSStop>(data['stops.txt']!)
            .then(gtfsStops => gtfsStops.map(
                stop => Stop.fromGTFS(stop)
            ))
        return {
            data: stops.reduce(
                (prev, curr) => {
                    prev[curr.id] = curr
                    return prev
                },
                {} as Record<string, MGTFSStop>
            )
        }
    }

    toGTFS (): MGTFSStops {
        return {
            data: Object.keys(this.data).reduce(
                (prev, curr) => {
                    prev[curr] = this.data[curr]!.toMGTFS()
                    return prev
                },
                {} as Record<string, MGTFSStop>
            )
        }
    }
    

    get (id: string): Stop | undefined {
        return this.data[id]
    }
}