import type { StopContinuity, StopType, Time, Timepoint } from '../types'
import {
    fromStopContinuity,
    fromStopType,
    fromTimepoint,
    toStopContinuity,
    toStopType,
    toTimepoint
} from '../types'
import { parseOptionalFloat, parseOptionalInt, parseTime } from '../util'


export type GTFSStopTime = {
    dropoff_booking_rule_id?: string
    location_id?: string
    location_group_id?: string
    pickup_booking_rule_id?: string
    stop_id?: string
    trip_id?: string
    arrival_time?: string
    continuous_drop_off?: string
    continuous_pickup?: string
    departure_time?: string
    drop_off_type?: string
    end_pickup_drop_off_window?: string
    pickup_type?: string
    shape_dist_traveled?: string
    start_pickup_drop_off_window?: string
    stop_headsign?: string
    stop_sequence: string
    timepoint?: string
}


export type MGTFSStopTime = {
    dropoff_booking_id?: string
    location_id?: string
    location_group_id?: string
    pickup_booking_id?: string
    stop_id?: string
    trip_id?: string
    arrival_time?: string
    departure_time?: string
    dist_traveled?: number
    dropoff_continuity?: number
    dropoff_type?: number
    end_pickup_dropoff?: string
    headsign?: string
    index: number
    pickup_continuity?: number
    pickup_type?: number
    start_pickup_dropoff?: string
    timepoint: number
}


export default class StopTime {

    dropoffBookingId?: string
    locationId?: string
    locationGroupId?: string
    pickupBookingId?: string
    stopId?: string
    tripId?: string
    arrivalTime?: string
    departureTime?: string
    distTraveled?: number
    dropoffContinuity?: StopContinuity
    dropoffType?: StopType
    endPickupDropoff?: string
    endTime: Time
    headsign?: string
    index: number
    pickupContinuity?: StopContinuity
    pickupType?: StopType
    startPickupDropoff?: string
    startTime: Time
    timepoint: Timepoint

    constructor (data: MGTFSStopTime) {
        this.dropoffBookingId = data.dropoff_booking_id
        this.locationId = data.location_id
        this.locationGroupId = data.location_group_id
        this.pickupBookingId = data.pickup_booking_id
        this.stopId = data.stop_id
        this.tripId = data.trip_id
        this.arrivalTime = data.arrival_time
        this.departureTime = data.departure_time
        this.distTraveled = data.dist_traveled
        this.dropoffContinuity = data.dropoff_continuity ? 
            toStopContinuity(data.dropoff_continuity) : undefined
        this.dropoffType = data.dropoff_type ?
            toStopType(data.dropoff_type) : undefined
        this.endPickupDropoff = data.end_pickup_dropoff
        this.headsign = data.headsign
        this.index = data.index
        this.pickupContinuity = data.pickup_continuity ?
            toStopContinuity(data.pickup_continuity): undefined
        this.pickupType = data.pickup_type ?
            toStopType(data.pickup_type): undefined
        this.startPickupDropoff = data.start_pickup_dropoff
        this.timepoint = toTimepoint(data.timepoint)

        const endTimeString = this.departureTime ?? this.endPickupDropoff
        const startTimeString = this.arrivalTime ?? this.startPickupDropoff
        if (!endTimeString || !startTimeString) {
            throw new Error(
                `StopTime for stop ${this.stopId ?? 'unknown'} on trip ` +
                `${this.tripId ?? 'unknown'} is missing required time fields`
            )
        }
        this.endTime = parseTime(endTimeString)
        this.startTime = parseTime(startTimeString)
    }

    static fromGTFS (data: GTFSStopTime): MGTFSStopTime {
        return {
            ...data,
            dropoff_booking_id: data.dropoff_booking_rule_id,
            pickup_booking_id: data.pickup_booking_rule_id,
            dist_traveled: parseOptionalFloat(
                data.shape_dist_traveled, 
                undefined
            ),
            dropoff_continuity: parseOptionalInt(
                data.continuous_drop_off,
                undefined
            ),
            dropoff_type: parseOptionalInt(
                data.drop_off_type,
                undefined
            ),
            end_pickup_dropoff: data.end_pickup_drop_off_window,
            headsign: data.stop_headsign,
            index: parseInt(data.stop_sequence),
            pickup_continuity: parseOptionalInt(
                data.continuous_pickup,
                undefined
            ),
            pickup_type: parseOptionalInt(
                data.pickup_type,
                undefined
            ),
            start_pickup_dropoff: data.start_pickup_drop_off_window,
            timepoint: parseOptionalInt(
                data.timepoint,
                fromTimepoint('exact')
            )
        }
    }

    toMGTFS (): MGTFSStopTime {
        return {
            dropoff_booking_id: this.dropoffBookingId,
            location_id: this.locationId,
            location_group_id: this.locationGroupId,
            pickup_booking_id: this.pickupBookingId,
            stop_id: this.stopId,
            trip_id: this.tripId,
            arrival_time: this.arrivalTime,
            departure_time: this.departureTime,
            dist_traveled: this.distTraveled,
            dropoff_continuity: this.dropoffContinuity ?
                fromStopContinuity(this.dropoffContinuity) : undefined,
            dropoff_type: this.dropoffType ?
                fromStopType(this.dropoffType) : undefined,
            end_pickup_dropoff: this.endPickupDropoff,
            headsign: this.headsign,
            index: this.index,
            pickup_continuity: this.pickupContinuity ?
                fromStopContinuity(this.pickupContinuity) : undefined,
            pickup_type: this.pickupType ?
                fromStopType(this.pickupType) : undefined,
            start_pickup_dropoff: this.startPickupDropoff,
            timepoint: fromTimepoint(this.timepoint)
        }
    }

}