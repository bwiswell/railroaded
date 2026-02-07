export const parseDate = (date: string): Date => new Date(Date.parse(date))


export const parseOptionalDate = (date?: string): Date | undefined =>
    date ? parseDate(date) : undefined


export const parseOptionalInt = 
    <T extends number | undefined>(value: string | undefined, dfault: T): T =>
        value ? parseInt(value) as T : dfault

    
export const parseOptionalFloat = 
    <T extends number | undefined>(value: string | undefined, dfault: T): T =>
        value ? parseFloat(value) as T : dfault