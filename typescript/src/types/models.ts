export type GTFSCalendar = {
    service_id: string
    end_date: string
    friday: number
    monday: number
    saturday: number
    start_date: string
    sunday: number
    thursday: number
    tuesday: number
    wednesday: number
}


export type GTFSCalendarDate = {
    service_id: string
    date: string
    exception_type: number
}