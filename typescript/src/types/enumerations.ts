const fromEnumeration = <T extends string>(enumeration: readonly T[]) => 
    (value: T): number => enumeration.indexOf(value)

const toEnumeration = <T extends string>(enumeration: readonly T[]) => 
    (value: number): T => enumeration[value] as T


const accessibilities = [
    'unknown',
    'accessible',
    'not_accessible'
] as const
/**
 * An enumeration describing the accessibility of a transit location.
 */
export type Accessibility = typeof accessibilities[number]
export const fromAccessibility = fromEnumeration(accessibilities)
export const toAccessibility = toEnumeration(accessibilities)


const bikesAlloweds = [
    'unknown',
    'allowed',
    'disallowed'
] as const
/**
 * An enumeration indicating if bikes are allowed on a trip.
 */
export type BikesAllowed = typeof bikesAlloweds[number]
export const fromBikesAllowed = fromEnumeration(bikesAlloweds)
export const toBikesAllowed = toEnumeration(bikesAlloweds)


const exceptionTypes = ['add', 'remove'] as const
/**
 * An enumeration describing the type of a calendar date exception.
 */
export type ExceptionType = typeof exceptionTypes[number]
export const fromExceptionType = fromEnumeration(exceptionTypes)
export const toExceptionType = toEnumeration(exceptionTypes)


const locationTypes = [
    'stop_or_platform',
    'station',
    'entrance_or_exit',
    'generic_node',
    'boarding_area'
] as const
/**
 * An enumeration describing the nature of a transit location.
 */
export type LocationType = typeof locationTypes[number]
export const fromLocationType = fromEnumeration(locationTypes)
export const toLocationType = toEnumeration(locationTypes)


const stopContinuities = [
    'continuous',
    'none',
    'via_phone',
    'via_driver'
] as const
/**
 * An enumeration describing the stop continuity of a route.
 */
export type StopContinuity = typeof stopContinuities[number]
export const fromStopContinuity = fromEnumeration(stopContinuities)
export const toStopContinuity = toEnumeration(stopContinuities)


const stopTypes = [
    'scheduled',
    'none',
    'via_phone',
    'via_driver'
] as const
/**
 * An enumeration describing the type of the stop.
 */
export type StopType = typeof stopTypes[number]
export const fromStopType = fromEnumeration(stopTypes)
export const toStopType = toEnumeration(stopTypes)


const timepoints = ['approximate', 'exact'] as const
/**
 * An enumeration indicating if a stop time is exact or approximate.
 */
export type Timepoint = typeof timepoints[number]
export const fromTimepoint = fromEnumeration(timepoints)
export const toTimepoint = toEnumeration(timepoints)


const transitTypes = [
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
export const fromTransitType = fromEnumeration(transitTypes)
export const toTransitType = toEnumeration(transitTypes)