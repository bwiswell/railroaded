export const formatDate = (date: Date): string => {
    const options = { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit' 
    } as const
    return date.toLocaleDateString('en-CA', options).replace(/\//g, '-')
}

export const formatOptionalDate = (date?: Date): string | undefined =>
    date ? formatDate(date) : undefined

export function includesDay (day: Date, dates: Date[]): boolean {
    return dates.some(date => isSameDay(day, date))
}

export function isSameDay (dateA: Date, dateB: Date): boolean {
    return (
        dateA.getFullYear() === dateB.getFullYear() &&
        dateA.getMonth() === dateB.getMonth() &&
        dateA.getDate() === dateB.getDate()
    );
}

export const parseDate = (date: string): Date => new Date(Date.parse(date))

export const parseOptionalDate = (date?: string): Date | undefined =>
    date ? parseDate(date) : undefined