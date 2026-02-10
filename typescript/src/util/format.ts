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