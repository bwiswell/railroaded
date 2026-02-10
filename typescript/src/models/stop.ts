import type { Accessibility, LocationType } from '../types'
import { 
    fromAccessibility, 
    toAccessibility, 
    fromLocationType, 
    toLocationType 
} from '../types'
import { parseOptionalFloat, parseOptionalInt } from '../util'


export type GTFSStop = {
    stop_id: string
    level_id?: string
    parent_id?: string
    zone_id?: string
    location_type?: string
    name?: string
    platform_code?: string
    stop_code?: string
    stop_desc?: string
    stop_lat?: string
    stop_lon?: string
    stop_timezone?: string
    stop_url?: string
    tts_stop_name?: string
    wheelchair_boarding?: string
}


export type MGTFSStop = {
    id: string
    level_id?: string
    parent_id?: string
    zone_id?: string
    accessibility: number
    code?: string
    desc?: string
    lat?: number
    lon?: number
    name: string
    platform_code?: string
    timezone?: string
    tts_name?: string
    type: number
    url?: string
}


export default class Stop {

    id: string
    levelId?: string
    parentId?: string
    zoneId?: string
    accessibility: Accessibility
    code?: string
    desc?: string
    lat?: number
    lon?: number
    name: string
    platformCode?: string
    timezone?: string
    ttsName?: string
    type: LocationType
    url?: string

    constructor (data: MGTFSStop) {
        this.id = data.id
        this.levelId = data.level_id
        this.parentId = data.parent_id
        this.zoneId = data.zone_id
        this.accessibility = toAccessibility(data.accessibility)
        this.code = data.code
        this.desc = data.desc
        this.lat = data.lat
        this.lon = data.lon
        this.name = data.name
        this.platformCode = data.platform_code
        this.timezone = data.timezone
        this.ttsName = data.tts_name
        this.type = toLocationType(data.type)
        this.url = data.url
    }

    static fromGTFS (data: GTFSStop): MGTFSStop {
        return {
            ...data,
            id: data.stop_id,
            accessibility: parseOptionalInt(
                data.wheelchair_boarding,
                fromAccessibility('unknown')
            ),
            code: data.stop_code,
            desc: data.stop_desc,
            lat: parseOptionalFloat(data.stop_lat, undefined),
            lon: parseOptionalFloat(data.stop_lon, undefined),
            name: data.name ?? 'unnamed',
            timezone: data.stop_timezone,
            tts_name: data.tts_stop_name,
            type: parseOptionalInt(
                data.location_type,
                fromLocationType('stop_or_platform')
            ),
            url: data.stop_url
        }
    }

    toMGTFS (): MGTFSStop {
        return {
            id: this.id,
            level_id: this.levelId,
            parent_id: this.parentId,
            zone_id: this.zoneId,
            accessibility: fromAccessibility(this.accessibility),
            code: this.code,
            desc: this.desc,
            lat: this.lat,
            lon: this.lon,
            name: this.name,
            platform_code: this.platformCode,
            timezone: this.timezone,
            tts_name: this.ttsName,
            type: fromLocationType(this.type),
            url: this.url
        }
    }

}