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


const exceptionTypes = ['add', 'remove'] as const
/**
 * An enumeration describing the type of a calendar date exception.
 */
export type ExceptionType = typeof exceptionTypes[number]
export const fromExceptionType = fromEnumeration(exceptionTypes)
export const toExceptionType = toEnumeration(exceptionTypes)


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