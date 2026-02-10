import type { GTFSAgency, MGTFSAgency } from '../models'
import { Agency } from '../models'
import { loadList } from '../util'


export type MGTFSAgencies = {
    data: Record<string, MGTFSAgency>
}


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
    
    agencies: Agency[]
    data: Record<string, Agency>
    ids: string[]

    constructor (data: MGTFSAgencies) {
        this.data = Object.keys(data.data).reduce(
            (prev, curr) => {
                prev[curr] = new Agency(data.data[curr]!)
                return prev
            },
            {} as Record<string, Agency>
        )
        this.agencies = Object.values(this.data)
        this.ids = Object.keys(this.data)
    }

    
    static async fromGTFS (
                data: Record<string, string>
            ): Promise<MGTFSAgencies> {
        const agencies = await loadList<GTFSAgency>(data['agency.txt']!)
            .then(gtfsAgencies => gtfsAgencies.map(
                agency => Agency.fromGTFS(agency)
            ))
        return {
            data: agencies.reduce(
                (prev, curr) => {
                    prev[curr.id] = curr
                    return prev
                },
                {} as Record<string, MGTFSAgency>
            )
        }
    }

    toGTFS (): MGTFSAgencies {
        return {
            data: Object.keys(this.data).reduce(
                (prev, curr) => {
                    prev[curr] = this.data[curr]!.toMGTFS()
                    return prev
                },
                {} as Record<string, MGTFSAgency>
            )
        }
    }
    

    get (id: string): Agency | undefined {
        return this.data[id]
    }
}