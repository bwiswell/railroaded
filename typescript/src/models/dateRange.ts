export type GTFSDateRange = {
    service_id: string
    end_date: string
    friday: boolean
    monday: boolean
    saturday: boolean
    start_date: string
    sunday: boolean
    thursday: boolean
    tuesday: boolean
    wednesday: boolean
}

export type MGTFSDateRange = {
    end: string
    schedule: boolean[]
    start: string
}


export default class DataRange {

    end: Date
    schedule: boolean[]
    start: Date

    constructor (data: MGTFSDateRange) {
        this.end = new Date(Date.parse(data.end))
        this.schedule = data.schedule
        this.start = new Date(Date.parse(data.start))
    }

    static fromGTFS (data: GTFSDateRange): MGTFSDateRange {
        return {
            ...data,
            end: data.end_date,
            start: data.start_date,
            schedule: [
                data.monday,
                data.tuesday,
                data.wednesday,
                data.thursday,
                data.friday,
                data.saturday,
                data.sunday
            ]
        }
    }

    toMGTFS (): MGTFSDateRange {
        const options = { 
            year: 'numeric', 
            month: '2-digit', 
            day: '2-digit' 
        } as const
        return {
            end: this.end.toLocaleDateString('en-CA', options)
                .replace(/\//g, '-'),
            schedule: this.schedule,
            start: this.start.toLocaleDateString('en-CA', options)
                .replace(/\//g, '-'),
        }
    }
}