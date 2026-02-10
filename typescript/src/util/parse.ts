import type { Time } from '../types'


export const parseDate = (date: string): Date => new Date(Date.parse(date))


export const parseOptionalDate = (date?: string): Date | undefined =>
    date ? parseDate(date) : undefined


export const parseOptionalInt = 
    <T extends number | undefined>(value: string | undefined, dfault: T): T =>
        value ? parseInt(value) as T : dfault

    
export const parseOptionalFloat = 
    <T extends number | undefined>(value: string | undefined, dfault: T): T =>
        value ? parseFloat(value) as T : dfault


export const parseTime = (time: string): Time => {
    var hours = parseInt(time.slice(0, 2))
    const days = Math.floor(hours / 24)
    hours = hours - days * 24
    const minutes = parseInt(time.slice(3, 5))
    const seconds = parseInt(time.slice(6, 8))
    const timestamp = (
        seconds +
        minutes * 60 +
        hours * 60 * 60 +
        days * 24 * 60 * 60
    )
    return {
        days,
        hours: hours >= 24 ? 0 : hours,
        minutes,
        raw: time,
        seconds,
        timestamp
    }
}