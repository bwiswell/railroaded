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