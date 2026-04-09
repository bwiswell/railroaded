import type { Time } from '../types'

import StopTime, { GTFSStopTime, MGTFSStopTime } from "./stopTime"


export type MGTFSTimetable = {
    data: Record<string, MGTFSStopTime>
}


export default class Timetable {

    data: Record<string, StopTime>
    end: StopTime
    start: StopTime
    stopIds: string[]
    stops: StopTime[]

    constructor (data: MGTFSTimetable) {
        this.data = Object.keys(data.data).reduce(
            (prev, curr) => ({ 
                ...prev,
                [curr]: new StopTime(data.data[curr]!) 
            }),
            {} as Record<string, StopTime>
        )
        this.stops = Object.values(this.data).sort(
            (a: StopTime, b: StopTime) => a.index - b.index
        )
        this.end = this.stops[this.stops.length - 1]!
        this.start = this.stops[0]!
        this.stopIds = Object.keys(this.data)
    }

    static fromGTFS (stops: GTFSStopTime[]): MGTFSTimetable {
        return {
            data: stops.reduce(
                (prev, curr) => {
                    if (!curr.stop_id) return prev
                    return {
                        ...prev,
                        [curr.stop_id]: StopTime.fromGTFS(curr)
                    }
                },
                {} as Record<string, MGTFSStopTime>
            )
        }
    }

    toMGTFS (): MGTFSTimetable {
        return {
            data: Object.keys(this.data).reduce(
                (prev, curr) => ({
                    ...prev,
                    [curr]: this.data[curr]!.toMGTFS()
                }),
                {} as Record<string, MGTFSStopTime>
            )
        }
    }


    get (id: string): StopTime | undefined { return this.data[id] }


    between (start: Time, end: Time): boolean {
        return (
            this.start.startTime.timestamp <= end.timestamp &&
            this.end.endTime.timestamp >= start.timestamp
        )
    }

    connects (stopAId: string, stopBId: string): boolean {
        return (
            this.through(stopAId) &&
            this.through(stopBId) &&
            this.data[stopAId]!.index < this.data[stopBId]!.index
        )
    }

    through (stopId: string): boolean { return this.stopIds.includes(stopId) }

}